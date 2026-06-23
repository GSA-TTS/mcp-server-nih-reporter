# NIH Grant Application Types (Activity Code Type Digits)

**Source:** NIH Grants Policy Statement  
**Use when:** A query involves filtering, identifying, or explaining NIH grant application types by their single-digit (or two-character) type code.

---

## Overview

Every NIH grant has an **application type code** — a 1–2 character prefix that identifies the stage and nature of the funding request. These codes appear as the first character(s) of an activity code (e.g., the `1` in `1R01`, the `5` in `5R01`).

---

## Application Type Reference Table

| Code | Name | Description |
|------|------|-------------|
| `1` | New | Initial request for support of a project not yet funded. |
| `2` | Renewal (Competing Continuation) | Initial request for additional funding for a period subsequent to a current award. Competes with all other peer-reviewed applications and must be developed as fully as a new application. If an unfunded renewal and its resubmission are both not funded, the applicant must use type `1` to pursue further funding; continuity with the prior award is not retained. |
| `3` | Competing Revision (Competing Supplement) | Request for additional funds during a current project period to support new or expanded activities not in the current award. Reflects scope expansion and requires peer review. Replaces the older NIH term "competing supplement." |
| `4C` | Competing Extension | Request for additional years of support beyond the years previously awarded. Used only for select programs. |
| `4N` | Noncompeting Extension | Request for additional years of support beyond the years previously awarded. Used only for select programs. |
| `5` | Noncompeting Continuation | Request or award for a subsequent budget period within a previously approved project. Does not require competition with other applications. |
| `6` | Change of Organization Status (Successor-in-Interest) | Transfer of rights and obligations under a grant incidental to the transfer of all assets of the recipient, or the portion of assets involved in grant performance. |
| `7` | Change of Recipient or Training Institution | Transfer of legal and administrative responsibility for a grant-supported project from one legal entity to another before the approved project period ends. |
| `8` | Change of Institute or Center (Noncompeting) | Change of the awarding NIH institute or center for a noncompeting continuation (type `5`). |
| `9` | Change of Institute or Center (Renewal) | Change of the awarding NIH institute or center for a renewal (type `2`). |

---

## Key Distinctions

- **Competing vs. noncompeting:** Types `1`, `2`, and `3` go through peer review and compete for funding. Types `5`, `6`, `7`, `8`, and `9` do not compete.
- **Type 2 vs. Type 1 after failed renewal:** If a Type `2` renewal and any resubmission both fail, the applicant must file a new Type `1`; they cannot retain continuity with the prior award.
- **Type 3 vs. Type 2:** A Type `3` is for *additional activities within a current period* (scope expansion); a Type `2` is for *a new period after the current one ends* (continuation of the whole project).
- **Type 4C vs. 4N:** Both extend years beyond what was originally awarded. The `C` variant is competing; the `N` variant is noncompeting.
- **Types 6, 7, 8, 9 are administrative:** These do not reflect new scientific activity — they handle organizational, institutional, or administrative changes to an existing award.

---

## Usage Rules

- Match user-supplied type codes **case-insensitively** and accept both the numeric code (`4C`, `5`) and common names (`renewal`, `noncompeting continuation`).
- When a user provides a plain-English term, map it to the appropriate code using the table above before filtering.
- If the intent is ambiguous (e.g., "extension" could be `4C` or `4N`), return results for **both** unless the user specifies competing or noncompeting.
- Do **not** invent or guess type codes outside this list.
