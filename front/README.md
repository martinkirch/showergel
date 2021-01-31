# Front-end development

The front-end is written in TypeScript packed with [Yarn](https://yarnpkg.com/),
with [VueJS](https://vuejs.org/)' [single-file components](https://v3.vuejs.org/guide/single-file-component.html).
We use the [Bulma](https://bulma.io/) CSS Framework and
[Material Design Icons](https://materialdesignicons.com/).

A fully-working HTML/JS/CSS build is included in this repository.
To modify the front-end, you must beforehand install Yarn and [Vue CLI](https://cli.vuejs.org/),
then run `yarn install` from the repository root.
When you're done, run `yarn build` and commit modifications in the `/showergel/www/` folder.

Linting will be triggered before the commit,
you may run it manually with `yarn lint`.
See also [this VSCode configuration hint](https://code.visualstudio.com/docs/setup/linux#_visual-studio-code-is-unable-to-watch-for-file-changes-in-this-large-workspace-error-enospc).
