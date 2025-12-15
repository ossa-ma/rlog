Raycast requires the use of `npm`. And must compile its own `node_modules`.

We chose `pnpm` for the monorepo because `npm` does not allow no-hoist which conflicts with the above.

Have to remove `raycast` from `pnpm-workspace.yaml` and root level `package.json` to allow it to be managed independently with `npm`.