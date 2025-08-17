function slimElement(element) {
    // slim down element to what we need to avoid reactivity bloat
    const elementKeys = [
        "description",
        "run_records"
    ];

    return elementKeys.reduce((obj, key) => ({ ...obj, [key]: element[key] }), {});
}

obj_orig = {'description': 'abc', 'a': ' aa'};

obj_new = slimElement(obj_orig);

console.log(obj_new);

