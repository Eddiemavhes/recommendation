const fs = require('fs');
const path = require('path');
const postcss = require('postcss');
const tailwind = require('tailwindcss');
const autoprefixer = require('autoprefixer');

const input = path.resolve(__dirname, '../static/css/tailwind.css');
const output = path.resolve(__dirname, '../static/css/styles.css');

const css = fs.readFileSync(input, 'utf8');

postcss([tailwind, autoprefixer])
  .process(css, { from: input, to: output })
  .then(result => {
    fs.writeFileSync(output, result.css);
    if (result.map) fs.writeFileSync(output + '.map', result.map.toString());
    console.log('Built', output);
  })
  .catch(err => {
    console.error(err);
    process.exit(1);
  });
