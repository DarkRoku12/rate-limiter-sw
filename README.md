## Requirements

See [./requirements.md](requirements.md)

## Implemented features

See [./features.md](features.md)

## Usage

### Installation 
Only Python 3.12+ is required.

### Running
Just execute the `main.py` file, _examples_:
- `python main.py` -> Interactive console stdin until EOF (`ctrl+d` / `ctrl+z`, os dependant)
- `python main.py < input.txt` -> Buffers the sample file `input.txt` to the program.

### Tests
Run `python -m unittest --verbose`
Alternatively, run `python tests.py`

## Technical considerations

__Programming language choice__

Python. 

Why not? While I'd feel more fluent coding in other languages, like TypeScript, and considering the performance
of pure Python (CPython) is not great. 

Then, why? This language has all the tools in the standard library to implement
a good proof-of-concept rate-limiter, we can further extend it by implementing multi-threading, benchmarking
memory usage / statistics and determine when it is a good time to free inactive client resources.

Later, when we got a solid implementation, we can move it Rust, Go, or even Zig.

__Algorithm choice__

A `sliding window algorithm` that implements a `bounded deque`, this is, a deque with a fixed limit that must remove the 1st element once we add a new element at last (`push`/`push_back`/`append`/`appendRight`).

Sliding window is the only one that allows us to track request to any arbitrary 60-seconds time window, without blocking the limit or exceeding it.

Since the window limit is rather small, window allocation per client won't be a concern, and the window is large enough (60 seconds) to allow bursts. We got both flexibility and low memory usage, considering the parameters of this exercise.

<u>A different thing</u> would be needing a very high request threshold, let say 600req/window, given another business requirement that may involve a large number of clients doing many requests per window and that window is rather small (10 seconds or less, I'd estimate),
in that scenario, algorithms like `Fixed Sliding Window` / `Token Bucket` / or a combination (maintaining 2 windows, one previous (`fixed`) + one filling against time past (`token`)), any of the three would be a better implementation.

Why? Since they'll require much less memory per client, and given that the no. of allowed requests is high and window length is low, a time bucket will refill quickly and a fixed window will reset quickly as well, giving less time to exploit those window boundaries to go over the threshold.

Given the aforementioned requirement, I'd imagine the nature of those requests comes closer to a low-level protocol like TCP/UDP with bare data and small packages, or a high-level protocol designed for speed/real-time like WebSocket, webRTC or Protobuf.

The `requirements.md` document mentions the potential usage of a High-precision time handling, and time handling is required
for Token Bucket, or, if instead of replying events like in this exercise, we're using the current time, this is often better called `High Resolution Clock` (languages like C++, JavaScript and PHP prefer this term).

Rust documentation is a good starting point for appropriate system calls, and we can look for a parallel in any other languages.
<br> Rust sources:
- https://doc.rust-lang.org/std/time/struct.Instant.html
- https://doc.rust-lang.org/std/time/struct.SystemTime.html

__Memory and complexity considerations__

A `deque` was chosen because it aligns well for a sliding window, we only really care of times within the considering given frame,
if the queue is not full, we can simply allow the request, else (if full) we allow or discard it whether the new request is outside
the window of the 1st (index=0) request, then push, the bounded deque behavior will discard this one last timing and append the new one (if request is allowed), or just leave the deque untouched and deny the request.

<u>So we care about</u>: Fast insertion at last (right end), fast deletion of 1st element, and as bounded memory management.

For this particular use case: "when timestamp could be slightly out of order", sorting would be less efficient than an array (not really much the case of a dynamic language like Python), but we only need one way sorting and most of the time it won't be needed, so this is not really a concern, but most of a unreal edge case (I don't see this particular requirement happening in real life).

Deques can be implemented using either a <u>linked list</u>, actually, [this is CPython internal implementation](https://github.com/python/cpython/blob/1b293b60067f6f4a95984d064ce0f6b6d34c1216/Modules/_collectionsmodule.c#L80-L84), or using <u>ring buffers</u>.

In other languages, we may need to 'pop after insert when full', or using a library that supports this kind of behavior, for example, [this one in Rust](https://docs.rs/bounded-vec-deque/latest/bounded_vec_deque/struct.BoundedVecDeque.html) claims to do this as well.

<u>As for memory management</u>, this is not an issue until we're close to run out of memory and crash, or the remaining memory may not
be enough to handle a sudden burst in traffic. Allocating and deallocating memory arbitrarily takes a good time and doing it frequently
may cause to much memory fragmentation.

It will be only critical to deallocate inactive clients once we reach a threshold we may not feel comfortable.
There is a reason why [Java](https://programming-language-benchmarks.vercel.app/problem/binarytrees) (and other languages featuring a VM) are faster than compiled languages in the binary tree benchmark. This is because VM languages tends to allocate a large portion of memory and the creation of new heap objects will be cheap since memory is already assigned. 

This doesn't happen in compiled languages as they are allocating memory on every 'new' call, we could see this in the [Zig](https://github.com/hanabi1224/Programming-Language-Benchmarks/blob/5628a75a538ca24ec034508b27af2fc59418a4b2/bench/algorithm/binarytrees/1.zig#L69-L77) implementation.

When considering [other benchmarks](https://benchmarksgame-team.pages.debian.net/benchmarksgame/performance/binarytrees.html) site for a similar/equal benchmark that has other 'optimized implementations', we can see that all top implementations are using a memory pool. An [outstanding read about memory allocators can be found here](https://github.com/tarantool/tarantool/wiki/LuaJIT-3.0-new-Garbage-Collector#block-allocator), as a part of a new garbage collector proposed for LuaJIT (credits to Mike Pall). 


## Author

Enmanuel Reynoso. <br>
Blog: http://code.darkroku12.ovh/ <br>
LinkedIn: https://linkedin.com/in/enmanuelr <br>