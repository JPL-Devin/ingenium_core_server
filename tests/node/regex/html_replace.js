'use strict';

const fs = require('fs');
const assert = require('assert');
const tokenize = require('html-tokenize');
const through = require('through2');
const { Readable } = require("stream");
const _ = require('lodash');

var construct_regexp = function (search_for, match_case, whole_word) {
  let regexp = null;
  let search_for_escaped = _.escapeRegExp(search_for);
  if (match_case && whole_word) {
    regexp = new RegExp(`\\b(${search_for_escaped})\\b`, 'g');
  } else if (!match_case && whole_word) {
    regexp = new RegExp(`\\b(${search_for_escaped})\\b`, 'ig');
  } else if (match_case && !whole_word) {
    regexp = new RegExp(`(${search_for_escaped})`, 'g');
  } else if (!match_case && !whole_word) {
    regexp = new RegExp(`(${search_for_escaped})`, 'ig');
  }
  return regexp;
}



var search_with_regex = function (input, regexp) {
  let match_items = [];

  let matches = input.matchAll(regexp);
  
  for (const match of matches) {
    // console.log(match);
    
    let match_str = match[0]
    
    let start_index = match.index;
    let length = match_str.length;
    let end_index = start_index + length;
    
    //console.log(`found: ${match_str} start_index: ${start_index} length: ${length}`);
    //console.log(`match_str: ${match_str}`);
    assert(input.substr(start_index, length) === match_str);
    
    match_items.push({
      text: match_str,
      start_index: start_index,
      length: length
    });
  }
  
  return match_items;
}



var replace_with_regex = function (input, regexp, replace_with) {
  return input.replace(regexp, replace_with);
}

var tokenize_html = async function (input) {
  return await new Promise((resolve, reject) => {
    let tokens = [];
    let s = new Readable({read(size) {
      this.push(input)
      this.push(null)
    }});
    
    let start_index = 0;
    
    let tokenized = s.pipe(tokenize())
    tokenized.pipe(through.obj(function (row, enc, next) {
        // convert stream to string
        let token_str = row[1].toString();
        row[1] = token_str;
        // console.log(row);
        let token = {
          type: row[0],
          value: token_str,
          start_index: start_index
        };
        tokens.push(token);
        start_index += token_str.length;
        next();
    }));
    tokenized.on('error', (err) => {
      reject(err);
    });
    tokenized.on('finish', () => {
      resolve(tokens);
    });
  });
}


var find_matches = async function (input, regexp) {
  let tokens = [];
  try {
    tokens = await tokenize_html(input);
  } catch (err) {
    log.warning(err);  
  }
  
  const matches = [];
  
  for (const token of tokens) {
    if (token.type === 'text') {
      let match_items = search_with_regex(token.value, regexp);
      for (const match_item of match_items) {
        matches.push({
          text: match_item.text,
          start_index: match_item.start_index + token.start_index,
          length: match_item.length
        });
      }
    }
  }
  return matches;
}

var replace_matches = async function (input, regexp, replace_with) {
  let tokens = [];
  try {
    tokens = await tokenize_html(input);
  } catch (err) {
    log.warning(err);  
  }
  
  const texts = [];
  
  for (const token of tokens) {
    if (token.type === 'text') {
      let token_updated = replace_with_regex(token.value, regexp, replace_with);
      texts.push(token_updated);
    } else {
      texts.push(token.value);
    }
  }
  return texts.join('');
}


let html_input = `
<body>This is inside body.
<div>
This is inside div. line.
Another line is division lined. text.
</div>
Another line inside line body.
</body>
`;


(async function test1 () {
  let regexp = construct_regexp('line', false, false);
  let match_texts = await find_matches(html_input, regexp);
  
  console.log(`num matches: ${match_texts.length}`);
  for (const match_text of match_texts) {
    console.log(html_input.substr(match_text.start_index, match_text.length));
  }
  console.log(JSON.stringify(match_texts, 0, 2));
  
  let html_output = await replace_matches(html_input, regexp, 'abc');
  console.log(html_output);

})();



