## Lab 7 - tuples and garbage collection (optional)

Goal: extend the compiler to *Lvec*: tuples, element access, `is` and
`len`, allocated on a heap that is collected.

This lab is optional and comes in three parts. Part 1 alone is a
working compiler for the book's `Lvec`; the only thing it does not do
is reclaim memory.

| part | what it adds | what it needs |
|---|---|---|
| 1 | tuples, no collector | no type checker, no root stack |
| 2 | + the collector      | both, and the pointer mask |
| 3 | + `t[0] = x`         | interpreter for testing |

Do part 1 first and stop there if you like. It is much smaller than
the lecture makes the stage look: with no collector there is no room
check, hence no new blocks, no root stack, and **register allocation
does not change at all**.

## Lvec --- what is new

Concrete syntax, on top of `Lfun`:

```
Type ::= ... | tuple[Type, ...]
exp  ::= ... | exp, ..., exp | exp[int] | len(exp)
cmp  ::= ... | is
```

From Python's `ast`:

```
Tuple([exp, ...], Load())
Subscript(exp, Constant(int), Load() | Store())
Call(Name('len'), [exp])
Compare(exp, [Is()], [exp])
```

Three things to get right in the shapes:

- `Subscript.ctx` tells a read from a write. In parts 1 and 2 only
  `expose_allocation` produces `Store()`, but every pass that matches
  `Subscript` must match the context too, or the two look identical.
- `Call(Name('len'), [_])` must be matched **before** the general
  `Call` case, exactly as `input_int` and `print` already are. `len`
  is not a user function - there is no label to call.
- `Tuple` also appears with `Store()` in real Python (`a, b = t`). We
  do not support unpacking; reject it.

Add tuples, indexing, `is` and `len` to the interpreter.

### Three restrictions

Reject these with a message rather than compiling something wrong:

- **the index must be a literal integer.** `t[i]` needs the offset
  *and* the element's type to be known statically.
- **at most 50 elements.** The length gets six bits of the tag (see
  below).
- **no `t[0] = x`** until part 3; it is not Python anyway.

### `is` and CPython

`is` on tuples compares addresses, and assignment copies an address,
so `t1 = t2` makes two names for one tuple.

Careful when you test this: CPython folds two equal **all-constant**
tuple literals into one object, so

```python
t1 = 3, 7
t3 = 3, 7
print(1 if t1 is t3 else 0)
```

prints `1` under CPython and `0` under your compiler - and your
compiler is the one that is right. Write every `is` test with at least
one non-constant element (`x = 3; t1 = x, 7`) and the two agree. Do not
put the book's aliasing program in your test suite verbatim: it fails
against CPython, and the failure looks exactly like a compiler bug.

## Part 1 --- tuples that leak

### A heap in runtime.c

A large static buffer and a `free_ptr` that only goes up:

```c
static long heap[1 << 20];       /* 8 MB */
long *free_ptr = heap;
```

No `collect`, no root stack, no `initialize`. Check that a
hand-written `.s` which bumps `free_ptr` and stores through it links
and runs.

### expose_allocation

A new pass, and the only new pass. It runs **before**
`remove_complex_operands` and rewrites each tuple literal into pieces
the back end can emit:

```python
(e0, ..., e(n-1))
```
⟹
```python
begin:
    x0 = e0                 # every element first
    ...
    x(n-1) = e(n-1)
    v = allocate(n)         # reserve the words, write the tag
    v[0] = x0               # then initialise
    ...
    v[n-1] = x(n-1)
    v
```

The order matters even here, and matters much more in part 2: an
element expression may itself allocate, and (once there is a
collector) an allocated-but-uninitialised tuple must never be
reachable during a collection. Elements first, allocation last.

Note what this pass does **not** introduce: `begin`, assignment and
element access are all constructs earlier passes already understand.
`allocate` is a new leaf. That is why the pass can sit before RCO and
emit ordinary complex expressions - everything downstream sorts them
out.

`allocate` belongs in the intermediate language, beside `Begin` and
`Goto`; a small dataclass with a `length` field.

### remove_complex_operands

- `allocate` and element access are **complex**;
- element access's operands must be **atoms**;
- `len`'s operand must be an atom.

Two things that will bite:

- **RCO now has to read a `Begin`.** Until now it only ever *produced*
  them. Its statements have to stay where they are rather than being
  hoisted into temporaries - the temporaries list holds
  `(Name, expression)` pairs, and a store is not one.
- your ANF checker needs a case for each new node. `allocate` has no
  `_fields`, so a generic visit walks straight past it and the check
  silently passes.

### explicate_control

Nothing. Really: an assignment whose target is a subscript already
matches the ordinary assignment case, and `allocate` and element
access reach the same default as any other right-hand side. If you
find yourself adding cases here, look at whether the ones you have are
too narrow.

A tuple literal should not change the number of basic blocks in part
1. That is worth checking - it is the whole part 1 / part 2
difference in one number.

### select_instructions

```
lhs = allocate(n)     =>  movq free_ptr(%rip), %r11
                          addq $8(n+1), free_ptr(%rip)
                          movq $tag, 0(%r11)
                          movq %r11, lhs

lhs = tup[n]          =>  movq tup, %r11
                          movq 8(n+1)(%r11), lhs

tup[n] = rhs          =>  movq tup, %r11
                          movq rhs, 8(n+1)(%r11)

lhs = (a is b)        =>  cmpq b, a
                          sete %al
                          movzbq %al, lhs

lhs = len(tup)        =>  movq tup, %r11
                          movq 0(%r11), lhs
                          sarq $1, lhs
                          andq $63, lhs
```

`free_ptr(%rip)` is RIP-relative addressing of a global; you should
already have a node for it. `is` reuses the comparison you wrote in
lab 4 with condition code `e` - a tuple's value *is* its address, so
identity is equality. `len` reads the tag back and is the only reason
`sarq` and `andq` appear.

In part 1 the tag is just the length:

```python
tag = 1 | (n << 1)
```

**Why `%r11` and not `%rax`.** `%r11` is reserved (it is not in the
register pool), and `patch_instructions` uses `%rax` to repair
instructions with two memory operands. A spilled store becomes

```
    movq -16(%rbp), %r11
    movq -8(%rbp), %rax
    movq %rax, 8(%r11)
```

which is correct only because the base register is not the one the
patch pass is free to overwrite. Compiling everything to the stack is
the quickest way to see this sequence.

### Checkpoint

- `v1 = (42,); v2 = (v1,); print(v2[0][0])` - the book's example.
- a tuple with mixed element types, read on both branches of an `if`.
- a tuple built in a function and returned to its caller.
- an aliasing program using `is` (with a non-constant element, see
  above).
- `len` of a tuple of tuples.
- everything still passes with register allocation *and* with every
  variable spilled to the stack.

That is part 1 finished: a compiler for `Lvec` that never frees
anything.

## Part 2 --- add the collector

### The runtime

The collector is a second program, and every bug in it shows up as
what looks like a miscompilation. Take the book's `runtime.c` and
exercise it **standalone** - a C `main` that builds a few tuples by
hand and calls `collect` - before any compiler output touches it.

The interface:

```c
void initialize(uint64_t rootstack_size, uint64_t heap_size);
void collect(int64_t** rootstack_ptr, uint64_t bytes_requested);

int64_t*  free_ptr;
int64_t*  fromspace_end;
int64_t** rootstack_begin;
```

Make the two sizes a compiler flag. The defaults are large; the test
that proves the collector runs needs a heap small enough to force
several collections.

### A type checker

Two questions cannot be answered at run time, because integers are not
tagged:

```python
node.has_type          # on every Tuple node: for the pointer mask
var_types[name]        # per function: for the spilling rule
```

So this is where a type checker stops being optional. It runs right
after `shrink` - `main` exists by then, and `and`/`or` are gone.

Note where each of the two is used. `has_type` is needed by
`expose_allocation`, which is still working on the source AST, so the
one run after `shrink` gives it. `var_types` is needed by the register
allocator, long after `explicate_control` has invented variables the
source never named - so either keep the environment alive that far, or
type-check the C-level program too.

No inference: `int`, `bool`, `tuple[...]`, `Callable[...]`, and the
annotations we have been writing since lab 6 and throwing away. So the
first job is to stop throwing them away - carry parameter and return
types on the function definition, and make a missing annotation an
error.

`ast` hands you `tuple[int, bool]` as a `Subscript` of a `Name`, so
write a small `parse_type` and keep types as your own dataclasses.

The arity check you wrote by hand in lab 6 ought to become a special
case of this - but only if you write it. Checking a call by walking
arguments and parameters together stops at the shorter of the two, and
then `f(1)` type-checks against a two-parameter `f`. Compare the
lengths first. Keep the hand-written check until the checker really
subsumes it.

### The pointer mask

```
 63       57 56                        7 6      1 0
+-----------+---------------------------+--------+-+
|  unused   |       pointer mask        | length |1|
+-----------+---------------------------+--------+-+
```

```python
tag = 1 | (n << 1) | (mask << 7)
```

Bit *i* of the mask is 1 if element *i* is itself a tuple. Bit 0 of
the tag is 1 while the tuple has not been copied; when it is 0 the
whole word is a forwarding pointer.

Unit-test the tag function: `tuple[int]` is `3`, `tuple[tuple[int]]`
is `131`.

### The room check

`expose_allocation` gains the conditional it did not have in part 1:

```python
    if free_ptr + bytes < fromspace_end:
        pass
    else:
        collect(bytes)
    v = allocate(n, type)
```

where *bytes* is `8 * (n + 1)`. Note where it sits: after the
elements, before the allocation. `allocate` itself never collects.

```
collect(bytes)        =>  movq %r15, %rdi
                          movq $bytes, %rsi
                          callq collect
```

Every tuple literal now costs two extra blocks. A program that builds
tuples in a loop gets a much bigger CFG, which the liveness fixpoint
walks repeatedly.

### Root frames

`%r15` points at the top of the root stack, which grows **up**.

Per function, on top of what lab 6 emits:

```att
    movq $0, <each root slot this function claims>
    addq $<8 * root spills>, %r15
    ...
    subq $<the same>, %r15
```

and in `main` only, before that:

```att
    movq $<rootstack size>, %rdi
    movq $<heap size>, %rsi
    callq initialize
    movq rootstack_begin(%rip), %r15
```

Two things to be careful about:

- **the zeroing is not optional.** The first tuple creation in the
  body can call `collect` before any root slot has been written, and
  the collector will follow whatever was there.
- **the root frame is not part of the 16-byte alignment computation.**
  That covers `pushq %rbp`, the callee-saved pushes and the ordinary
  spill area. The root stack is a different stack, adjusted through
  `%r15`, with no alignment requirement. Add it to the frame size and
  every call is misaligned.

Get this working with **every variable spilled** before touching the
register allocator. That is the checkpoint that matters: a collecting
compiler, before the allocator has a say.

### Register allocation

Two additions, both in the interference graph and the home
assignment; the colouring itself does not change.

1. **A tuple-typed variable live across a call must spill.** At every
   `callq` - not just `callq collect`, since any callee may allocate -
   add edges from each live tuple-typed variable to the *callee-saved*
   registers as well. The caller-saved edges are already there, so no
   colour is left in the pool and the variable spills.
2. **Tuple variables spill to `%r15`,** everything else to `%rbp`.

The second one has a trap. Your existing code probably maps a spill
colour to a home; now the mapping is `(colour, is it a tuple) -> home`
and it needs **two independent counters**, each remembered per colour
so that two variables sharing a colour still share a home. A tuple
variable and an integer variable may legitimately get the same colour
- they do not interfere - and must then get different homes, one on
each stack. Use one counter and they overlap.

### Checkpoint

- a tuple live across a call gets a home at `-8(%r15)`; an integer
  live across the same call gets a callee-saved register.
- the prelude zeroes exactly as many root slots as the function
  spilled.
- a function with both kinds of spill still has a 16-byte aligned
  frame.
- a loop that allocates, with a heap small enough to collect several
  times, keeps one tuple live throughout and still prints the right
  answer.
- a tuple live across a *recursive* call - root frames have to nest.

## Part 3 --- add mutation

`t[0] = x` in the source. The instruction sequence already exists -
`expose_allocation` has been emitting stores since part 1 - so the
work is in the type checker, RCO and `explicate_control`, and it is
small.

What actually changes is the **oracle**: CPython raises `TypeError` on
a write to a tuple, so it can no longer run these programs. Compare
against an interpreter instead, in which tuples are Python lists.

Switch the oracle *first*, and check that the part 1 and 2 programs
still pass against it, before writing anything mutable. That check is
the point: an interpreter is a second implementation of the language,
and the two easy ways to get it wrong are both about statements rather
than tuples. Executing a `while` by recursing on
`body + [loop] + rest` costs a Python stack frame per statement
executed, so a few hundred iterations exhaust the stack; and printing
without a newline gives output that no longer lines up with the
compiled binary's.

A side benefit once it works: the interpreter's tuples are distinct
objects, so `is` behaves properly there and the constant-folding caveat
above goes away.

## Stretch goals

- **Where does the time go?** Count collections and bytes copied; plot
  against heap size.
- **Generational collection** - most tuples die young, so collect the
  young ones more often.
- **Arrays**: the same tag, but neither the length nor the index is
  known at compile time. Work out what breaks: the offset computation,
  the element type, and bounds checks.
