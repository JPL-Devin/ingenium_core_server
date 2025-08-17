const fs = require('fs');

function test0() {
  const regex_str = `src=\\\\"([\\s\\S]*?)\\\\"`;
  console.log(regex_str);
  const regex_pattern = new RegExp(regex_str, 'g');  
  input = `abc src=\\"abc.gif\\" more src=\\"abc.png\\" some`;
  
  replace_pattern = 'src=\\"here/$1\\"'
  
  output = input.replace(regex_pattern, replace_pattern);
  
  console.log(input);
  console.log(output);
}


// const regex_pattern = /src\=\\"([\s\S]*?)\/file_server\/ingenium-media-prod-psyche\/([\s\S]+?)\\"/g

function test1() {
  // THIS NEEDS TO BE UPDATED
  const source_bucket = 'ingenium-media-prod-psyche';
  const target_bucket = 'ingenium-media-prod-psyche-atlo';
  
  const regex_str = `src="([\\s\\S]*?)/file_server/${source_bucket}/([\\s\\S]+?)"`;
  console.log(regex_str);
  const regex_pattern = new RegExp(regex_str, 'g');
  let input = fs.readFileSync('input.txt', 'utf8');
  console.log(input);
  console.log(typeof input);
  
  replace_pattern = `src="/file_server/${target_bucket}/$2"`
  output = input.replace(regex_pattern, replace_pattern);
  
  console.log('');
  console.log(output);
  
  fs.writeFileSync('output.txt', output, 'utf-8');  
}

function test2() {
  const source_bucket = 'ingenium-media-prod-psyche';
  
  const regex_str = `src="([\\s\\S]*?)/file_server/${source_bucket}/([\\s\\S]+?)"`;
  //console.log(regex_str);
  const regex_pattern = new RegExp(regex_str, 'g');
  console.log(regex_pattern);
  let input = fs.readFileSync('input.txt', 'utf8');
  console.log(input);
  console.log(typeof input);
  
  replace_pattern = `src="/file_server/${source_bucket}/$2"`;
  console.log(replace_pattern);
  output = input.replace(regex_pattern, replace_pattern);
  
  console.log('');
  console.log(output);
  
  fs.writeFileSync('output.txt', output, 'utf-8');  
  
  const match_str = `src="/file_server/${source_bucket}/([\\s\\S]+?)"`;
  // console.log(match_str);
  const match_pattern = new RegExp(match_str, 'g');
  console.log(match_pattern);
  
  const matches = output.match(match_pattern);
  
  console.log('matches:');
  for (const match of matches) {
    console.log(match);
  }
  
  console.log('paths:');
  for (const match of matches) {
    console.log(match.substring(5, match.length-1));
  }  
}


// test1();
test2();

