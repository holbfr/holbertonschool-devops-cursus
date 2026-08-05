---

# Module 0 — Why Production Images Matter

This module answers one question:

> **Why should I care about image optimization at all?**

Most beginners think Docker images are just "packages" containing an application.

Production engineers think differently.

A Docker image is:

* a deployment artifact
* a security boundary
* a distribution package
* a cached filesystem
* an immutable snapshot

If your image is bad, deployments become slower, CI pipelines become slower, cloud costs increase, and security risks grow.

Let's understand why.

---

## Lesson 0.1 — "It Works on My Machine"

Suppose Alice writes an application.

She runs

```bash
npm install
npm start
```

Everything works.

She pushes her code.

Bob clones the repository.

Bob runs

```bash
npm install
```

Now everything breaks.

Why?

Because Alice's machine contains things Bob's doesn't.

Examples:

* different Node version
* different OS
* different libraries
* different environment variables
* cached dependencies
* local configuration

This is where the famous sentence comes from:

> "It works on my machine."

Docker solves this by packaging the environment together with the application.

Instead of sharing:

```
Source Code
```

You share

```
Operating System

+ Runtime

+ Dependencies

+ Application
```

Now everyone executes exactly the same environment.

---

### Question

Why is sharing only source code sometimes insufficient?

Think before reading the answer.

### Answer

Because source code depends on an environment.

Without the same environment:

* different dependency versions
* missing libraries
* incompatible runtimes

can all produce different behavior.

Docker standardizes the environment.

---

# Lesson 0.2 — Why Small Images Matter

Imagine two Docker images.

Image A

```
120 MB
```

Image B

```
2.3 GB
```

They run exactly the same application.

Which one should you choose?

Most beginners answer:

> "The smaller one because it saves disk space."

That's only one reason.

There are many more.

---

## Faster Downloads

Whenever Kubernetes starts a new container, it first downloads the image.

Downloading

```
120 MB
```

is much faster than

```
2.3 GB
```

If you deploy hundreds of containers every day, those seconds add up to hours.

---

## Lower Cloud Costs

Container registries charge for storage and network transfer.

A smaller image means

* less storage
* less bandwidth
* cheaper deployments

---

## Better CI/CD

Every CI pipeline usually does

```
Build

↓

Push

↓

Pull

↓

Deploy
```

Every one of those steps transfers the image.

A smaller image accelerates the entire pipeline.

---

## Smaller Attack Surface

Imagine two houses.

House A has

* 2 doors
* 4 windows

House B has

* 47 doors
* 90 windows

Which one offers more opportunities for burglars?

The second one.

Software works similarly.

Every package you install could contain:

* vulnerabilities
* outdated software
* unnecessary executables
* forgotten credentials

The more software inside your container, the larger the attack surface.

---

### Question

Does a smaller image automatically mean it is more secure?

Think first.

### Answer

No.

A smaller image **reduces the attack surface**, but security also depends on:

* package versions
* configuration
* user permissions
* secrets management
* network policies

Small images are usually *easier* to secure, but they are not automatically secure.

---

# Lesson 0.3 — What's Inside an Image?

Many people imagine a Docker image as a ZIP file.

It isn't.

A Docker image is more like a stack of transparent sheets.

Imagine placing transparent pages on top of each other.

Layer 1

```
Ubuntu
```

Layer 2

```
Node.js
```

Layer 3

```
Dependencies
```

Layer 4

```
Application
```

Docker combines all these layers into what appears to be one filesystem.

This idea is the foundation of Docker optimization.

We'll spend an entire module understanding layers because almost every optimization depends on them.

---

### Question

If two images both use Ubuntu, does Docker store Ubuntu twice?

Think.

### Answer

No.

Docker stores identical layers only once.

If Image A and Image B both begin with the same Ubuntu layer, they share it.

This layer sharing is one reason Docker is efficient.

---

# Lesson 0.4 — Why Build Tools Don't Belong in Production

Suppose you're baking cookies.

During baking you use:

* measuring cups
* mixing bowls
* rolling pin
* oven

After the cookies are finished...

Do you package the oven with every box of cookies?

Of course not.

The oven was necessary to *make* the cookies.

It isn't necessary to *eat* them.

Docker works exactly the same way.

During the build, you might need:

* gcc
* make
* Python
* build-essential
* npm
* cargo

Once the application has been built, those tools are no longer needed.

Leaving them inside the production image:

* increases image size
* increases vulnerabilities
* increases attack surface

This is exactly what **multi-stage builds** solve.

One image builds.

Another image runs.

Only the finished "cookies" are copied into the runtime image.

---

### Question

Why not simply uninstall the build tools after compiling?

Think carefully.

### Answer

Because Docker images are built in immutable layers.

If you install a compiler in one layer and remove it in a later layer, the bytes from the earlier layer are still part of the image history. The final filesystem no longer shows the compiler, but the image still contains the data from the layer where it was installed.

Multi-stage builds avoid this entirely by never copying the build layer into the runtime image.

We'll see exactly why when we study layers in Module 1.

---

# Lesson 0.5 — Why Pin Versions?

Consider this Dockerfile:

```dockerfile
FROM node:latest
```

You build it today.

Everything works.

Tomorrow, someone rebuilds the exact same Dockerfile.

Now the application crashes.

How?

Because `latest` is not a fixed version—it's just a moving label. Today it may point to Node 22, tomorrow to Node 23.

That means the same Dockerfile can produce different images on different days.

Using a pinned version such as:

```dockerfile
FROM node:22.17.0-slim
```

makes the build reproducible. If someone rebuilds it months later, they start from the same base image.

---

### Question

Is pinning versions only about preventing bugs?

### Answer

No. It also helps with:

* reproducible builds
* predictable deployments
* easier debugging
* controlled upgrades
* compliance and auditing

If a bug appears, you know exactly which base image was used.

---

# End-of-Module Check

By now, you should be able to answer these questions without looking them up:

1. Why does "it works on my machine" happen?
2. Besides saving disk space, why are small images valuable?
3. Why does installing unnecessary packages increase security risk?
4. Why don't build tools belong in production images?
5. Why is `FROM node:latest` considered a bad practice for production?
6. What does Docker gain by storing images as layers instead of one large archive?

If you can explain these concepts in your own words, you're building intuition rather than memorizing facts.

---

Excellent choice. This is **the most important module in Docker**. In fact, almost every optimization you will ever perform—multi-stage builds, cache optimization, image shrinking, `.dockerignore`, BuildKit—depends on understanding layers.

If Module 0 answered **"Why should we optimize?"**, then Module 1 answers **"How does Docker actually work internally?"**

The goal isn't to memorize Docker commands. The goal is to build a mental model that makes every Docker behavior predictable.

---

# Module 1 — Docker Images and Layers

---

# Lesson 1 — What Is a Docker Image?

## The Common Misconception

Ask a beginner:

> What is a Docker image?

Most answers sound like:

> "It's like a ZIP file."

This is understandable, but it's not how Docker thinks.

A Docker image is **not one big file**.

It is **a stack of immutable filesystem snapshots**.

Think of a Docker image as a pile of transparent sheets.

```
Application Files
-------------------------

Dependencies
-------------------------

Node Runtime
-------------------------

Ubuntu
-------------------------
```

When Docker runs the image, it combines these sheets into one filesystem that the container sees.

---

## Mental Model #1 — Transparent Sheets

Imagine writing on transparent plastic sheets.

Sheet 1:

```
/
├── bin
├── etc
├── usr
```

Sheet 2:

```
/
└── node
```

Sheet 3:

```
/
└── app
```

When stacked together, they appear as one filesystem.

The individual sheets still exist.

Docker calls these sheets **layers**.

---

## Why Is This Better?

Suppose you build three applications.

```
Image A

Ubuntu
Node
App A
```

```
Image B

Ubuntu
Node
App B
```

```
Image C

Ubuntu
Node
App C
```

Without layers:

```
Ubuntu stored 3 times

Node stored 3 times
```

With layers:

```
Ubuntu stored once

↓

Node stored once

↓

Three application layers
```

Docker saves enormous amounts of disk space.

---

## Knowledge Check

**Question**

Why doesn't Docker simply compress everything into one file?

Pause before reading.

---

### Answer

Because layers provide four major advantages.

**Storage Sharing**

Multiple images reuse common layers.

---

**Caching**

Unchanged layers don't need rebuilding.

---

**Incremental Downloads**

Only missing layers are transferred.

---

**Reproducibility**

Each layer has its own cryptographic digest.

Docker can verify every layer independently.

---

# Lesson 2 — Every Dockerfile Instruction Creates a Layer

This is probably the single most important rule in Docker.

Every instruction like:

```dockerfile
FROM ubuntu:24.04
RUN apt-get update
RUN apt-get install curl
COPY . .
CMD ["bash"]
```

creates a new filesystem layer (metadata-only instructions like `CMD`, `ENV`, or `LABEL` don't add filesystem content, but Docker still records them as image configuration/history).

Let's visualize it.

---

## Step 1

```dockerfile
FROM ubuntu:24.04
```

Image:

```
Ubuntu Layer
```

---

## Step 2

```dockerfile
RUN apt-get update
```

Docker starts a temporary container.

Runs:

```
apt-get update
```

Then saves everything that changed.

New layer:

```
Layer 2

Package index updated
```

---

## Step 3

```dockerfile
RUN apt-get install curl
```

Another container.

Another filesystem snapshot.

```
Ubuntu

↓

apt update

↓

curl installed
```

---

## Step 4

```dockerfile
COPY . .
```

Another layer.

```
Ubuntu

↓

apt update

↓

curl

↓

Application
```

Every instruction adds another layer.

---

## Important

Docker does **not** modify previous layers.

It only creates new ones.

That leads to our next concept.

---

# Lesson 3 — Immutable Layers

## What Does Immutable Mean?

Immutable means:

> Once created, it can never be changed.

Never.

Docker never edits existing layers.

Instead, it creates new ones.

---

Imagine writing in permanent marker.

Once the page is written, you can't erase it.

You can only place another transparent sheet on top.

Docker behaves exactly like that.

---

Suppose we have:

Layer 1

```
hello.txt
```

Contents:

```
Hello
```

Now another instruction:

```dockerfile
RUN echo "World" >> hello.txt
```

Docker does **not** modify Layer 1.

Instead it creates:

Layer 2

```
hello.txt

Hello

World
```

Layer 1 still exists unchanged.

---

## Why Is Immutability Good?

Imagine Docker modified existing layers.

Changing one file would require rebuilding every image that uses it.

Instead:

Layer 1 stays unchanged.

Only Layer 2 changes.

Much more efficient.

---

# Lesson 4 — Why Deleting Files Doesn't Shrink Images

This is one of the most surprising Docker behaviors.

Suppose you write:

```dockerfile
RUN apt-get install gcc
```

Image grows:

```
+300 MB
```

Later:

```dockerfile
RUN apt-get remove gcc
```

Most beginners think:

```
300 MB added

300 MB removed

Final image unchanged
```

Wrong.

---

The actual layer history is:

Layer 1

```
Ubuntu
```

Layer 2

```
gcc installed
+300 MB
```

Layer 3

```
gcc deleted
```

Layer 2 still exists.

Layer 3 only records:

> delete these files

The bytes from Layer 2 are still part of the image.

---

## Why?

Remember.

Layers cannot be modified.

Docker cannot go back in time.

It can only add another layer.

---

## This Explains Multi-stage Builds

Now the reason behind multi-stage builds becomes obvious.

Instead of:

```
Install compiler

Compile

Delete compiler
```

we use:

```
Builder Image

↓

Compile

↓

Copy output

↓

Runtime Image
```

The compiler layer is never copied.

Therefore it never exists in the final image.

---

## Knowledge Check

Question:

Why doesn't deleting files reduce image size?

---

Answer

Because deleting only creates another layer hiding those files.

The original layer containing the files still exists inside the image.

---

# Lesson 5 — Union Filesystems

This is the technology that makes Docker layers usable.

---

Suppose we have:

Layer 1

```
A
B
```

Layer 2

```
C
```

Layer 3

```
D
```

The container sees:

```
A

B

C

D
```

Even though these files physically exist in different layers.

Docker merges them.

This merged view is called a **Union Filesystem**.

---

Think of Photoshop.

One layer contains:

```
Sky
```

Another contains:

```
Mountains
```

Another contains:

```
Trees
```

You don't see three images.

You see one final picture.

Docker layers work the same way.

---

## File Replacement

Suppose Layer 1 has:

```
config.json
```

Layer 2 also has:

```
config.json
```

Which one wins?

The highest layer.

Lower layers become hidden.

They still exist.

They just aren't visible.

---

## Deleting Files

Deletion also works by hiding.

Docker creates a special marker called a **whiteout**.

Conceptually:

```
Layer 1

config.json
```

Layer 2

```
Delete config.json
```

The file still exists in Layer 1.

The Union Filesystem simply hides it from the final view.

---

# Lesson 6 — Inspecting Layers with `docker history`

Theory is useful.

Seeing it is better.

---

Build:

```dockerfile
FROM ubuntu:24.04

RUN apt-get update

RUN apt-get install -y curl

COPY hello.txt /

CMD ["bash"]
```

Now:

```bash
docker history IMAGE_NAME
```

Typical output:

```
IMAGE          CREATED      SIZE

CMD bash       0B

COPY hello     1KB

RUN install    18MB

RUN update     25MB

FROM ubuntu    80MB
```

Every line corresponds to one image layer or image configuration step.

---

## Reading the History

Notice:

```
COPY hello.txt

1 KB
```

Only one kilobyte changed.

Installing curl:

```
18 MB
```

Large filesystem change.

---

## Question

Which Dockerfile instruction produced the largest layer?

Answer:

Usually package installation.

Not copying source code.

---

# Lesson 7 — Docker Build Cache

Now we reach one of Docker's biggest performance features.

---

Suppose we build:

```dockerfile
FROM ubuntu

RUN apt-get update

RUN apt-get install curl

COPY . .

CMD ["bash"]
```

First build:

```
Everything executes.
```

Second build:

Docker compares each instruction.

```
Same instruction?

↓

Yes

↓

Reuse previous layer
```

This is called a **cache hit**.

---

## Cache Example

Build #1

```
RUN apt-get update

Executed
```

Build #2

```
RUN apt-get update

Cache hit
```

Docker skips the work.

---

## When Does Cache Break?

Imagine:

```dockerfile
COPY . .

RUN npm install
```

You modify:

```
README.md
```

Docker sees:

```
COPY changed
```

Everything after that instruction must be rebuilt.

Including:

```
npm install
```

Even though dependencies never changed.

This explains why Dockerfile instruction order matters so much.

We'll dedicate the next module to mastering cache-friendly Dockerfiles.

---

# Lab 1 — Watching Layers Being Created

Create:

```dockerfile
FROM ubuntu:24.04

RUN touch file1

RUN touch file2

RUN touch file3
```

Build it.

Run:

```bash
docker history IMAGE_NAME
```

### Questions

How many layers were created?

Why?

---

Expected Answer

One filesystem layer for each `RUN`, plus the base image.

---

# Lab 2 — Immutability

Dockerfile:

```dockerfile
FROM ubuntu:24.04

RUN dd if=/dev/zero of=/large.bin bs=1M count=100

RUN rm /large.bin
```

Build it.

Inspect:

```bash
docker history IMAGE_NAME
```

### Question

Did the image shrink?

Why not?

---

Expected Answer

No.

The delete operation only adds another layer that hides the file.

The 100 MB layer still exists underneath.

---

# Lab 3 — Cache Experiment

Dockerfile:

```dockerfile
FROM node:22-slim

WORKDIR /app

COPY . .

RUN npm install
```

Build twice.

Change:

```
README.md
```

Build again.

### Question

Why was `npm install` executed again?

---

Answer

Because the `COPY . .` layer changed.

Every following instruction lost its cache.

---

# Lab 4 — Shared Layers

Build:

```
Image A

FROM ubuntu
```

Build:

```
Image B

FROM ubuntu
```

Question

How many Ubuntu layers are stored?

Answer

One.

Both images reuse it.

---

# Common Misconceptions

### Misconception 1

> Every image is independent.

False.

Images share layers.

---

### Misconception 2

> Deleting files reduces image size.

False.

Deletion only hides files in later layers.

---

### Misconception 3

> Docker rebuilds everything every time.

False.

Docker reuses cached layers whenever possible.

---

### Misconception 4

> Layers are directories.

False.

They are immutable filesystem snapshots that Docker's storage driver combines into a unified view.

---

# End-of-Module Quiz

### Question 1

What is a Docker layer?

**Answer**

An immutable filesystem snapshot produced during the image build process. Multiple layers are combined to form the image's filesystem.

---

### Question 2

Why are layers immutable?

**Answer**

Immutability allows layers to be safely shared, cached, verified, and reused across images without risking accidental modification.

---

### Question 3

Why does deleting a file not reduce image size?

**Answer**

Because the original layer containing the file cannot be modified. Docker adds a new layer that hides the file, but the data remains in the earlier layer.

---

### Question 4

What is the purpose of a Union Filesystem?

**Answer**

It merges multiple immutable layers into a single, coherent filesystem that the container sees.

---

### Question 5

What information does `docker history` provide?

**Answer**

It shows the sequence of instructions that created the image, along with the size contribution of each layer or configuration step, helping identify where space is being used.

---

### Question 6

When can Docker reuse a cached layer?

**Answer**

When the instruction and all inputs that affect it (such as copied files, build arguments, or previous layers) are unchanged from a previous build.

---

### Question 7

Suppose you have this Dockerfile:

```dockerfile
FROM node:22-slim

WORKDIR /app

COPY . .

RUN npm install

RUN npm test

CMD ["npm", "start"]
```

You edit only `README.md`.

Which instructions are likely to be rebuilt?

**Answer**

`COPY . .` changes because the build context changed. As a result, `RUN npm install`, `RUN npm test`, and everything after the `COPY` must also be rebuilt, even though your application code and dependencies may not have changed.

---

# Key Takeaways

By the end of this module, you should have the following mental model:

* A Docker image is **a stack of immutable filesystem layers**, not a single archive.
* Most filesystem-changing Dockerfile instructions create a new layer; Docker never edits an existing one.
* The **Union Filesystem** merges those layers into the single filesystem your container sees.
* Deleting a file creates a hiding layer rather than removing bytes from earlier layers.
* `docker history` helps you inspect how an image was assembled and where space is consumed.
* Docker's build cache works at the layer level. Good Dockerfile design is largely about maximizing cache reuse.

With this foundation, the next module—**Build Context and `.dockerignore`**—will make much more sense, because you'll understand exactly why changing a seemingly unrelated file can invalidate cached layers and slow down your builds.
