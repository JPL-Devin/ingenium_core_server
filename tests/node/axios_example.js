var axios = require('axios');

async function test_run(url) {      
    try {
        response = await axios.get(url);
        console.log(`response.status: ${response.status}`);
        console.log(`response.data: ${JSON.stringify(response.data)}`);        
    }
    catch(err) {
        if (err.response) {
            if (typeof err.response.data == 'string') {
                console.log(`err.response.data: ${err.response.data}`);
            } else {
                console.log(`err.response.data: ${JSON.stringify(err.response.data, 0, 2)}`);
            }
            
            console.log(`err.response.status: ${err.response.status}`);
            console.log(`err.message: ${err.message}`);
            console.log(`err.stack: ${err.stack}`);
        } else {
            console.log(`err: ${JSON.stringify(err, 0, 2)}`);
        }        
    }
}

async function run_all() {
    console.log('-----');
    await test_run('http://localhost:8010/api/v5/health');
    
    console.log('-----');
    await test_run('http://localhost:8010/api/v5/health2');

    console.log('-----');
    await test_run('http://localhost123:8010/api/v5/health2');    
}

async function get_errors() {
  
    console.log('----- -----');
    try {
        await axios.get('http://localhost:8010/api/v5/health2');
    } catch (err) {
        let error_processed = push_error('High level error 1', err);
        console.log(`error_processed: ${JSON.stringify(error_processed, 0, 2)}`);
    }

    try {
        await axios.get('http://localhost123:8010/api/v5/health2');
    } catch (err) {
        let error_processed = push_error('High level error 2', err);
        console.log(`error_processed: ${JSON.stringify(error_processed, 0, 2)}`);
    }
}

function transform_axios_error(err) {
    let err_new = {
        message: '',
        details: [],
        error_type: '',
        error_source: '',
        http_code_at_source: -1
    };

    if (err.response) {
        if (typeof err.response.data == 'string') {
            err_new['message'] = err.response.data;
        } else {
            if (err.response.data) {
                if (err.response.data.hasOwnProperty('message')) {
                    err_new['message'] = err.response.data.message;
                }
                
                if (err.response.data.hasOwnProperty('details') && Array.isArray(err.response.data.details)) {
                    err_new['details'] = err.response.data.details;
                }
                
                if (err.response.data.hasOwnProperty('error_type')) {
                    err_new['error_type'] = err.response.data.error_type;
                } 
                
                if (err.response.data.hasOwnProperty('error_source')) {
                    err_new['error_source'] = err.response.data.error_source;
                }   
    
                if (err.response.data.hasOwnProperty('http_code_at_source')) {
                    err_new['http_code_at_source'] = err.response.data.http_code_at_source;
                }
            }
        }

        if (err_new['http_code_at_source'] == -1) {
            err_new['http_code_at_source'] =  err.response.status;
        }
    } 

    if (!err_new.message) {
        err_new['message'] = err.message;
    }
    if (err_new.details.length == 0) {
        err_new.details.push(err.stack);
    }
    return err_new;
}

function push_error(message, err) {
    let err_new = transform_axios_error(err);
    err_new.details.push(err_new.message);
    err_new.message = message;
    return err_new;
}

run_all();

// get_errors();



