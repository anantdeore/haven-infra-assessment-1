# AI conversation records

If you used an AI assistant for B2, put the record of that here before submitting (export,
screenshot-transcribed text, or your own written summary of the exchange) — see B2's section
in DESIGN_NOTES.md for what to cover. Leave this folder empty if you didn't use one.

B2. Build it
Build two things:
An access check so a Property Manager can only view screening reports for tenants under their own landlord account - not any other.
A cost-tagging check that fails if a resource is missing a landlord_account_id tag - the real billing unit - not tenant_id, which is what resources are tagged with today.
Must work:
A test proving the cross-account case is denied, and the same-account case is allowed.
The tag check is generic, not hardcoded to one example resource.
The tag check is idempotent - rerunning it on an unchanged plan gives the same result. State the exact key you used to determine that, in DESIGN_NOTES.md, using the word ‘idempotency’
Before writing any code: say out loud, on your recording, what you learned from the README that changes how you'd build this.

Modify/create only the necessary files in folder /scripts. 
do not share output over here
