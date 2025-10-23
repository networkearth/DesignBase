# DesignBase

## LLM's as "Compilers"

Code tells a compiler how to build something. LLMs can now build things. So what language should tell them what to build and how to build it?

Three things are required from this language:

1. **Precision** - You need to get what you expect.
2. **Consistency** - Someone else compiling it needs to get the same result.
3. **Readability** - Someone else needs to understand it and make updates.

The problem: LLMs are flexible, eager to please, and fill in gaps. You can write imprecise, context-driven statements that only make sense in the moment, and the LLM will probably build something. But this isn't really a language—you (or anyone else) won't be able to reproduce exactly what you did.

The solution: Think about how design documents actually get built.

A design document starts as a conversation. You map out what's needed, others point out what's vague or unclear, and together you clarify the design.

But the work doesn't end there. Even when everyone agrees on the first version, people talk past each other or make hidden assumptions. These surface as building begins. If you methodically update the design doc as these issues appear, you eventually arrive at something that precisely captures what everyone wanted—a repeatable guide that becomes language an LLM can compile.

Design docs should be a requirement in any real project—you should be writing them anyway. But what's fantastic is now you can compile your components straight from the design instead of writing code yourself which not only improves your productivity but actually allows you to use a much wider range of technologies and techniques.

Another advantage: LLMs are terrible at debugging their own work. More updates mean more spaghetti code. Being able to create things from scratch repeatedly lets the LLM do its best work. Win-win!

The result? Your primary output as an engineer shifts from codebase to "designbase" - design documents you maintain and recompile whenever you want.

## Component-Based Design

Designs get overwhelming fast. Even simple web apps have many pieces to build and connect. Representing everything in one place is a recipe for disaster, and keeping it all in your head leads to headaches. The key to good design is breaking things into a hierarchy of components.

### What Each Component Needs

- **Use Cases**: How the component can be used
- **Constraints**: Properties that must be met for correct operation
- **Interfaces**: How to call or use the component
  - Inputs: Specs for all inputs
  - Outputs: Specs for all outputs
  - Intermediates: Specs for byproducts like logs
- **Build**: What sub-components are used, how their interfaces connect

### Why These Matter

**Use Cases** ensure you understand what you're building. Without them, you can't build well or avoid breaking things.

**Interfaces** define how components fit into the ecosystem—they're the face of an otherwise black box.

**Constraints** specify what must work for the component to function.

**Build** defines how the component breaks down into sub-components, how to call those sub-components' interfaces in this specific context (with concrete parameters), and how data/control flows between them—a mini architecture. Forces you to break larger components into smaller, reusable pieces.

Together, these define *what* the component does, how it interfaces with others, and what constraints apply—but not *how* it works internally. That's left as a black box for implementation... except for the build. So why specify the build? Because forcing breakdown into smaller components drives precision and reuse, preventing components from becoming code-spaghetti monoliths.
