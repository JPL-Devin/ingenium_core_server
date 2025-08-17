var axios = require('axios');
var prompt = require('prompt');
var pprompt = require('password-prompt');
const { ownKeys } = require('core-js/fn/reflect');

async function test1() {
    // const {username} = await prompt.get(['username']);
    // const pw = pprompt('password: ');

    const {username, password} = await prompt.get({
        properties: {
            username: {
                message: 'username',
                hidden: false
            },
            password: {
                message: 'password',
                hidden: true
            }
        }
    }) 

    // console.log(`username: ${username} password: ${password}`);
    const server = 'http://localhost';
    let url = `${server}/auth_server/api/v2/login`;

    /*
    let options = {
        auth: {
            username: username,
            password: password,
        }
    };
    */
    console.log(`url: ${url}`)

    let auth = 'Basic ' + Buffer.from(username + ':' + password).toString('base64');

    console.log(`auth: ${auth}`);

    let res = await axios.get(url, {headers: {Authorization: auth}});
    console.log(`status: ${res.status}`);
    console.log(res.data);

    url = `${server}/core_server/api/v5/procedures/clipper-procedure-10411/versions`;

    let headers = {
        Authorization: `Bearer ${res.data.access_token}`
    }
    /*
    res = await axios.post(url, {version_author: username, version_description: 'some version'}, {headers: headers});
    console.log(`status: ${res.status}`);
    console.log(res.data);
    */
    axios.post(url, {version_author: username, version_description: 'some version1'}, {headers: headers});
    axios.post(url, {version_author: username, version_description: 'some version2'}, {headers: headers});
}

test1();



