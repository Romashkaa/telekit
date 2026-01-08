# Telekit DSL

**Telekit DSL** — this is a custom domain-specific language (DSL) used to create interactive pages, such as FAQs.  
It allows you to describe the message layout, add images, and buttons for navigation between pages in a convenient, structured format that your bot can easily process.

The parser and analyzer provide an excellent system of warnings and errors with examples, so anyone can figure it out!

```js
@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are answers to common questions to help you get started:";
    buttons {
        photo_demo("Image Example");
        navigation("Navigation Demo");
    }
}
```

- [Integration »](12_telekit_dsl_integration.md)
- [Syntax »](13_telekit_dsl_syntax.md)
- [Examples »](https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md#telekit-dsl)