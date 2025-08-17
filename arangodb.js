var avacado = require('arangojs');
var db = avacado('http://localhost:8529');
db.useBasicAuth('root', 'somepassword');
var collections = ["executionCollection", "executionEdges", "exeMetadata", "ResultOf", "Results", "stepOrder", "venue", "versionEdge"]
db.createDatabase('coredb', function (err, info) {
    if (err) console.error(err.stack);
    else {
    	db.useDatabase('coredb');
		db.edgeCollection('executionEdges').create(function(err, swag){
            db.collection("executionCollection").create(function(err, swag){
                db.collection("exeMetadata").create(function(err, swag){
                    db.edgeCollection("ResultOf").create(function(err, swag){
                        db.edgeCollection("stepOrder").create(function(err, swag){
                            db.collection("venue").create(function(err, swag){
                                db.edgeCollection("versionEdge").create(function(err, swag){
                                    
                                })
                            })
                        })
                    })
                }))
            })
        });
    	db.graph('coregraph').create({
    		edgeDefinitions: [
	        {
	            collection: 'coreedge',
	            from: ["vertices",'exeMetadata'],
	            to: ["vertices"]
	        },
            {
                collection: 'coreedge',
                from: ["vertices",'exeMetadata'],
                to: ["vertices"]
            }
	    ]
    	});
    }
});
