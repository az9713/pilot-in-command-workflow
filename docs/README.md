# PIC System Documentation

Welcome to the documentation for the PIC Agentic Organizational System. This folder contains everything you need to use and develop this system.

---

## Documentation Map

```
                              ┌─────────────────┐
                              │   START HERE    │
                              │   CLAUDE.md     │
                              │  (project root) │
                              └────────┬────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
   ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
   │  QUICK START    │        │   USER GUIDE    │        │ DEVELOPER GUIDE │
   │  (5 min intro)  │        │  (full usage)   │        │ (modify/extend) │
   └────────┬────────┘        └────────┬────────┘        └────────┬────────┘
            │                          │                          │
            │                          │                          ▼
            │                          │                 ┌─────────────────┐
            │                          │                 │  ARCHITECTURE   │
            │                          │                 │  (internals)    │
            │                          │                 └─────────────────┘
            │                          │
            └──────────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────────────────┐
            │         SUPPORT DOCUMENTS            │
            ├──────────────────────────────────────┤
            │  TROUBLESHOOTING - Fix problems      │
            │  GLOSSARY - Understand terms         │
            │  REFERENCE - Look up details         │
            └──────────────────────────────────────┘
```

---

## Choose Your Path

### "I'm New - Just Want to Try It"
1. Read [QUICK_START.md](QUICK_START.md) (5 minutes)
2. Follow the 10 examples
3. You're ready!

### "I Want to Use It Regularly"
1. Start with [QUICK_START.md](QUICK_START.md)
2. Read [USER_GUIDE.md](USER_GUIDE.md) for complete instructions
3. Bookmark [REFERENCE.md](REFERENCE.md) for quick lookups

### "I Want to Modify or Extend It"
1. Read [USER_GUIDE.md](USER_GUIDE.md) to understand usage
2. Read [CODEBASE_EXPLAINED.md](CODEBASE_EXPLAINED.md) to understand every file
3. Study [ARCHITECTURE.md](ARCHITECTURE.md) for design
4. Follow [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for changes

### "Something Isn't Working"
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
2. Look up error messages in [REFERENCE.md](REFERENCE.md)
3. Review [GLOSSARY.md](GLOSSARY.md) for unfamiliar terms

---

## Document Summaries

| Document | Pages | Purpose | Audience |
|----------|-------|---------|----------|
| [QUICK_START.md](QUICK_START.md) | ~10 | Get started fast, 10 examples | Everyone |
| [USER_GUIDE.md](USER_GUIDE.md) | ~25 | Complete usage instructions | Users |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | ~30 | Modify and extend system | Developers |
| [CODEBASE_EXPLAINED.md](CODEBASE_EXPLAINED.md) | ~50 | Every file explained in detail | Developers |
| [ARCHITECTURE.md](ARCHITECTURE.md) | ~15 | System design internals | Developers |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | ~15 | Fix common problems | Everyone |
| [GLOSSARY.md](GLOSSARY.md) | ~10 | Term definitions | Everyone |
| [REFERENCE.md](REFERENCE.md) | ~20 | Complete technical reference | Everyone |

---

## Quick Links

### For Users
- [How to start a workflow](QUICK_START.md#step-4-your-first-workflow)
- [Available commands](USER_GUIDE.md#using-commands)
- [Understanding phases](USER_GUIDE.md#the-six-phases-explained)
- [Making decisions](USER_GUIDE.md#working-with-decisions)

### For Developers
- [Project structure](DEVELOPER_GUIDE.md#project-structure)
- [Adding a new PIC](DEVELOPER_GUIDE.md#adding-a-new-pic-agent)
- [Creating skills](DEVELOPER_GUIDE.md#creating-new-skills)
- [Modifying hooks](DEVELOPER_GUIDE.md#modifying-hooks)

### For Troubleshooting
- [Quick diagnosis](TROUBLESHOOTING.md#quick-diagnosis)
- [Common errors](TROUBLESHOOTING.md#error-reference)
- [Recovery procedures](TROUBLESHOOTING.md#recovery-procedures)

---

## Documentation Standards

All documentation in this project follows these principles:

1. **Step-by-Step** - No steps are skipped
2. **Beginner-Friendly** - No assumed knowledge
3. **Complete** - Everything documented
4. **Practical** - Real examples, not just theory
5. **Searchable** - Clear headings and tables

---

## Keeping Documentation Updated

If you modify the system, update the relevant documentation:

| Change | Update These Docs |
|--------|-------------------|
| New command | USER_GUIDE, REFERENCE, QUICK_START |
| New phase | All docs mentioning phases |
| New config option | DEVELOPER_GUIDE, REFERENCE |
| Bug fix | TROUBLESHOOTING if relevant |
| New term | GLOSSARY |

---

## Feedback

If you find documentation that is:
- Unclear
- Missing steps
- Outdated
- Has errors

Please update it! Documentation is as important as code.
