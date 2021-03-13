# Front-end development

The front-end is written in JavaScript packed with [Yarn](https://yarnpkg.com/),
with [VueJS](https://vuejs.org/)' [single-file components](https://v3.vuejs.org/guide/single-file-component.html).
We use the [Bulma](https://bulma.io/) CSS Framework.

To modify the front-end, you must beforehand install Yarn and [Vue CLI](https://cli.vuejs.org/),
then run `yarn install` from the repository root.
Start the live-building server with `yarn serve`.
If you don't have time to install the whole back-end,
you can call the demo app by creating a ``front/.env`` file that contains::

    VUE_APP_BACKEND_URL=https://arcane-retreat-54560.herokuapp.com

Similarly, a fully-working HTML/JS/CSS build is included in this repository,
so one doesn't have to install ``yarn`` and Vue while working on the back-end.
When you're done, run `yarn build` and commit modifications in the `/showergel/www/` folder.

See also [this VSCode configuration hint](https://code.visualstudio.com/docs/setup/linux#_visual-studio-code-is-unable-to-watch-for-file-changes-in-this-large-workspace-error-enospc).
