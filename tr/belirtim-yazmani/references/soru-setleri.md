# Question sets (one round, at most 10 questions)

The goal is to obtain the facts the consultant forgot to write and the decisions that are **already made**. This file is a checklist, not a script: drop what the inputs already answer, merge close questions, and add the question this development obviously needs (for example "by which criterion and from which field is a risky supplier identified?"). Offer no options and no recommendations: instead of "should it be X or Y?" ask "has X been decided, and what is it?". Order the questions by section weight (3.5, 3.4, 6.1, 2.2, 3.3, 2.1, 2.5, 5.1 first). Every unanswered question becomes a marker and an OPEN row in 7.3. Ask in the user's language.

## Every type

| Question | Feeds section |
|---|---|
| In which application, by whom and through which steps is this work done today; at exactly which step is the problem? | 2.1 |
| What is the measurable effect and the volume of the problem (items/day, duration, error count)? Is there a real example document number and date? | 2.1 |
| Have the extension approach, the SAP technology to use and the target clean core level been decided; what is the decision? | 1.1, 2.2 |
| What is the scope boundary: which company codes, document types, channels are in; what is deliberately left out? | 2.5 |
| Which external team or system do we depend on; who verified the assumptions taken as true, and when? | 2.5 |
| If a step fails, what does the system do, what does the user see, who intervenes? | 3.5, 5.1 |
| Who will use the application; at which organizational level (company code, purchasing org, …) is an authorization restriction wanted? | 5.2, 5.3 |
| What real data can be used for testing (document number, master data, company code)? | 6.1 |
| Are the go-live date, the transport owner and the manual steps in each system known? | 7.2 |
| When something goes wrong in production, what is looked at: which events, logged where, for how long? | 7.1 |
| Who owns the remaining open topics and by when? | 7.3 |
| Is there a verified list of SAP objects (CDS view, API, BAdI, App ID) and a project naming standard? | 4.1 |

## R · Rapor

| Question | Section |
|---|---|
| Which are the selection fields; which are mandatory, what are their defaults and value helps? | 3.2 |
| What are the output columns, sorting, totals/subtotals and navigation targets? | 3.6 |
| What are the data volume and the acceptable response time? | 3.11 |
| Have the output type and the export need been decided? | 3.6 |

## I · Arayüz / API

| Question | Section |
|---|---|
| Have direction, protocol, format and authentication method been agreed with the counterpart; what is the endpoint? | 3.4, 3.10 |
| What is the trigger (event, job, user) and its frequency; what are the volume and the largest message size? | 3.4 |
| Is there a source for the field mapping (counterpart schema, sample message)? | 3.4 |
| What happens if the same message is sent or received twice; has the deduplication key been decided? | 3.9 |
| If the counterpart does not answer: have timeout, retry count and interval, and the give-up point been decided? | 3.9 |
| What are the counterpart's error codes and the expected behaviour for each; what is the SLA? | 3.10 |
| Who monitors and reprocesses failed messages, from which application? | 3.9, 7.1 |

## C · Dönüşüm

| Question | Section |
|---|---|
| What are the source system, file format, record count and load window? | 3.4, 3.11 |
| Who approved the transformation and cleansing rules; is there a mapping table? | 3.4 |
| What happens to a faulty record: skipped, or does the load stop; who receives the error report? | 5.1 |
| If the load is rerun, how are duplicate records prevented? | 3.9 |
| How is the reconciliation done after the load (count, amount check)? | 6.1 |

## E · Genişletme

| Question | Section |
|---|---|
| Which extension point will be used; has it been verified as released? | 4.3 |
| At which moment, for which document types and conditions does the logic run; in which cases is standard behaviour kept? | 3.5 |
| Does it change standard fields or fill custom fields; are the custom fields defined? | 4.2, 4.3 |
| Is there a limit on the impact on save time? | 3.5 (3.11 when the profile is `tam`) |

## F · Form

| Question | Section |
|---|---|
| Have the form technology, output channels (print, e-mail) and languages been decided? | 4.4 |
| Under which condition is it printed; what is the output determination rule? | 4.4 |
| Is there an approved sample output or field list; what are the logo, signature and legal text requirements? | 4.4 |

## W · İş akışı

| Question | Section |
|---|---|
| What are the steps and how is the approver determined at each step (role, amount threshold, organization)? | 2.3, 3.5 |
| What happens on rejection, send-back, delegation and timeout? | 2.3, 3.8 |
| Which fields may change during approval; does a change restart the flow? | 3.5 |
| Who receives which notification, and when? | 5.1, 7.1 |

## U · Fiori / UI5 uygulaması

| Question | Section |
|---|---|
| Have the floorplan and the UI approach (Fiori elements, freestyle) been decided; what are the OData version and the use of draft? | 1.2, 3.3 |
| Which screens, filters, columns and fields; which are editable, mandatory, conditionally visible? | 3.3, 3.7 |
| Which actions; when are they enabled, what does a user without authorization see? | 3.3, 5.3 |
| What are the record's states and allowed transitions? | 3.8 |
| What are the launchpad placement, devices and languages? | 3.3 |
