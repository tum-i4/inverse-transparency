import commonjs from "@rollup/plugin-commonjs";
import resolve from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import { config } from "dotenv";
import copy from "rollup-plugin-copy";
import livereload from "rollup-plugin-livereload";
import postcss from "rollup-plugin-postcss";
import svelte from "rollup-plugin-svelte";
import { terser } from "rollup-plugin-terser";
import svelteOptions from "./svelte.config";

const production = !process.env.ROLLUP_WATCH;

export default {
  input: "src/main.js",
  output: {
    sourcemap: true,
    format: "iife",
    name: "app",
    file: "public/build/bundle.js",
  },
  plugins: [
    replace({
      // stringify the object
      process: JSON.stringify({
        env: {
          ...config().parsed, // attached the .env config
        },
      }),
    }),
    svelte({
      ...svelteOptions,
      // enable run-time checks when not in production
      dev: !production,
      // we'll extract any component CSS out into
      // a separate file - better for performance
      css: (css) => {
        css.write("public/build/bundle.css");
      },
    }),

    postcss(),

    // If you have external dependencies installed from
    // npm, you'll most likely need these plugins. In
    // some cases you'll need additional configuration -
    // consult the documentation for details:
    // https://github.com/rollup/plugins/tree/master/packages/commonjs
    resolve({
      browser: true,
      dedupe: ["svelte"],
    }),
    commonjs(),
    copy({
      targets: [
        {
          src: "node_modules/bootstrap/dist/**/*",
          dest: "public/vendor/bootstrap",
        },
      ],
    }),

    // In dev mode, call `npm run start` once
    // the bundle has been generated
    !production && serve(),

    // Watch the `public` directory and refresh the
    // browser on changes when not in production
    !production && livereload("public"),

    // If we're building for production (npm run build
    // instead of npm run dev), minify
    production && terser(),
  ],
  watch: {
    clearScreen: false,
  },
};

function serve() {
  let started = false;

  return {
    writeBundle() {
      if (!started) {
        started = true;

        require("child_process").spawn("npm", ["run", "start", "--", "--dev"], {
          stdio: ["ignore", "inherit", "inherit"],
          shell: true,
        });
      }
    },
  };
}
