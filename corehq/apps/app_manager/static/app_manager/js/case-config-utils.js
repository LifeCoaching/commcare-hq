var CC_UTILS = {
    getQuestions: function (questions, filter, excludeHidden, includeRepeat, excludeTrigger) {
        // filter can be "all", or any of "select1", "select", or "input" separated by spaces
        var i, options = [],
            q;
        excludeHidden = excludeHidden || false;
        excludeTrigger = excludeTrigger || false;
        includeRepeat = includeRepeat || false;
        filter = filter.split(" ");
        if (!excludeHidden) {
            filter.push('hidden');
        }
        if (!excludeTrigger) {
            filter.push('trigger');
        }
        for (i = 0; i < questions.length; i += 1) {
            q = questions[i];
            if (filter[0] === "all" || filter.indexOf(q.tag) !== -1) {
                if ((includeRepeat || !q.repeat) && (!excludeTrigger || q.tag !== "trigger")) {
                    options.push(q);
                }
            }
        }
        return options;
    },
    getAnswers: function (questions, condition) {
        var i, q, o, value = condition.question,
            found = false,
            options = [];
        for (i = 0; i < questions.length; i += 1) {
            q = questions[i];
            if (q.value === value) {
                found = true;
                break;
            }
        }
        if (found && q.options) {
            for (i = 0; i < q.options.length; i += 1) {
                o = q.options[i];
                options.push(o);
            }
        }
        return options;
    },
    filteredSuggestedProperties: function (suggestedProperties, properties) {
        var used_properties = _.map(properties, function (x) {
            return x.key();
        });
        return _(suggestedProperties).difference(used_properties);
    },
    propertyDictToArray: function (required, property_dict, caseConfig, keyIsPath) {
        var property_array = _(property_dict).map(function (value, key) {
            return {
                path: !keyIsPath ? value : key,
                key: !keyIsPath ? key : value,
                required: false
            };
        });
        property_array = _(property_array).sortBy(function (property) {
            return caseConfig.questionScores[property.path] * 2 + (property.required ? 0 : 1);
        });
        return required.concat(property_array);
    },
    propertyArrayToDict: function (required, property_array, keyIsPath) {
        var property_dict = {},
            extra_dict = {};
        _(property_array).each(function (case_property) {
            var key = case_property[!keyIsPath ? 'key' : 'path'];
            var path = case_property[!keyIsPath ? 'path' : 'key'];
            if (key || path) {
                if (_(required).contains(key) && case_property.required) {
                    extra_dict[key] = path;
                } else {
                    property_dict[key] = path;
                }
            }
        });
        return [property_dict, extra_dict];
    }
};
