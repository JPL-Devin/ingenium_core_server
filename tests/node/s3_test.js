var AWS = require('aws-sdk');
var fs = require('fs');
var fse = require("fs-extra");
var path = require('path');

let init_params = {
    accessKeyId: process.env.FILE_SERVER_ACCESS_KEY,
    secretAccessKey: process.env.FILE_SERVER_SECRET_KEY,
    endpoint: process.env.FILE_SERVER_API_HOST ? process.env.FILE_SERVER_API_HOST : 'http://localhost:9000',
    s3ForcePathStyle: true, // needed with minio?
    signatureVersion: 'v4'
}

console.log('s3 init params:', init_params);

var s3_client = new AWS.S3(init_params);

const KEY = 'penguin22.jpeg';

var object_exists = function (bucket, key) {
    return new Promise((resolve, reject) => {
      let params = {
        Bucket: bucket,
        Key: key
      };
  
      s3_client.headObject(params, (err, meta_data) => {

        if (err) {
          console.log('object_exists err:', err);
          resolve(false);
        } else {  
          resolve(true);
        }
      });
    });
}

var upload_to_file_server = function (bucket, key, buffer) {
    return new Promise((resolve, reject) => {
      let params = {
        Body: buffer,
        Bucket: bucket,
        Key: key,
        ContentType: 'binary'
      };
  
      s3_client.putObject(params, (err) => {
        if (err) {
          let msg = 'Failed to upload file. reason: {0}'.format(util.inspect(err));
          reject({'message': msg});
        } else {
          bucket_key = path.join(bucket, key);
          resolve(bucket_key)
        }
      });
    });
}

var download_from_file_server = function (target_dir, bucket, key) {
    return new Promise((resolve, reject) => {
        const target_path = path.join(target_dir, bucket, key);
        const target_path_dirname = path.dirname(target_path);
        console.log('target_path_dirname:', target_path_dirname);
        fse.ensureDirSync(target_path_dirname);
        const params = { Bucket: bucket, Key: key }
        const s3_stream = s3_client.getObject(params).createReadStream();
        const file_stream = fs.createWriteStream(target_path);
        s3_stream.on('error', reject);
        file_stream.on('error', reject);
        file_stream.on('close', () => { resolve(target_path);});
        s3_stream.pipe(file_stream);
    });
}


const MEDIA_BUCKET = 'ingenium-media';

return new Promise(function(resolve, reject) {
    let params = {};
    s3_client.listBuckets(params, function(err, data) {
        if (err) {
            console.log(err, err.stack);
            reject(err);
        }
        else {
            console.log('listBuckets results:', data);
            let media_bucket = null;
            let buckets = data.Buckets;
            for (let i=0; i < buckets.length; i++) {
                let bucket = buckets[i];
                console.log('bucket.Name:', bucket.Name);
                if (bucket.Name == 'ingenium-media') {
                    media_bucket = bucket;
                    break;
                }
            }

            resolve(media_bucket);
        }       
    })
})
.then((media_bucket) => {
    console.log('media_bucket:', media_bucket);
    return new Promise(function(resolve, reject) {
        if (media_bucket == null) {
            console.log('Create media_bucket');
            let params = {
                Bucket: 'ingenium-media',
                //ACL: 'public-read',
                //GrantFullControl: 'STRING_VALUE',
                //GrantRead: 'STRING_VALUE',
                //GrantReadACP: 'STRING_VALUE',
                //GrantWrite: 'STRING_VALUE',
                //GrantWriteACP: 'STRING_VALUE'            
            };
            s3_client.createBucket(params, function(err, data) {
                if (err) {
                    console.log(err, err.stack);
                    reject(err);
                }
                else {
                    console.log(data);
                    resolve(data);
                }       
            })    
        } else {
            console.log('bucket already exists.');
            resolve(null);
        }
    })
})
.then((bucket_data) => {
    console.log('configure media_bucket bucket_data:', bucket_data);
    /*
    {
        "Version":"2012-10-17",
        "Statement":[
            {
                "Effect":"Allow",
                "Principal": {
                    "AWS":["*"]
                },
                "Action":["s3:GetBucketLocation","s3:ListBucket"],
                "Resource":["arn:aws:s3:::mybucket"]
            },
            {
                "Effect":"Allow",
                "Principal":{
                    "AWS":["*"]
                },
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::mybucket/*"]
            }
        ]
    }    
    */
    let bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Sid": "Public",
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": [
              "s3:GetObject",
              "s3:GetBucketLocation"
            ],
            "Resource": [
              `arn:aws:s3:::${MEDIA_BUCKET}/*`, `arn:aws:s3:::${MEDIA_BUCKET}`
            ]
          }
        ]
    };

    return new Promise(function(resolve, reject) {
        if (bucket_data != null) {
            console.log('Configure media_bucket');
            let params = {
                Bucket: 'ingenium-media',
                Policy: JSON.stringify(bucket_policy)            
            };
            s3_client.putBucketPolicy(params, function(err, data) {
                if (err) {
                    console.log(err, err.stack);
                    reject(err);
                }
                else {
                    console.log('Bucket policy was updated', data);
                    resolve(data);
                }       
            })    
        } else {
            resolve();
        }
    })
})
.then(() => {
    return new Promise(function(resolve, reject) {
        fs.readFile(path.resolve(__dirname, 'penguin.jpeg'), function(err, file_data) {     
            if (err) {
                console.log(err);
                reject(err);
            } else {
                resolve(file_data);
            }
        });
    })
    .then((file_data) => {
        console.log('Got the file. Now upload it');
        return upload_to_file_server(MEDIA_BUCKET, KEY, file_data)
    })
})
.then(() => {
    object_exists('ingenium-media', KEY)
    .then((exists) => {
        console.log('object exists:', exists);
    })
    .catch((err) => {
        console.log('err:', err);
    })
})
.then(() => {
    download_from_file_server('/tmp/t2', MEDIA_BUCKET, KEY )
    .then((res) => {
        console.log('res:', res);
    })
    .catch((err) => {
        console.log('err:', err);
    })
})

