var axios = require('axios');

async function main() {
  let res = await axios.get('http://localhost/auth_server/api/v2/login', {
    auth: {
      username: '',
      password: ''
    },
    validateStatus: false
  });

  if (res.status === 200) {
    console.log(JSON.stringify(res.data));
  } else {
    console.log('login failed');
    return;
  }

  const elem_id = '7f0e6b1f-8ace-400c-8225-798ba963e382';
  const url = `http://localhost/core_server/api/v5/procedures/clipper-procedure-11219/custom_script_steps/${elem_id}/input`;

  const options = {
    headers: {
      Authorization: `Bearer ${res.data.access_token}`
    }
  }
  for (let i=0; i < 10; i++) {
    const payload = {
      timeout: 240 + i
    };
    axios.post(url, payload, options).then(res => {console.log(`status: ${res.status}`);});
  }
}

main();

