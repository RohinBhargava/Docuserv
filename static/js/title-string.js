jQuery.extend( jQuery.fn.dataTableExt.oSort, {
    "title-string-asc": function (str1, str2) {
        if(str1 == "")
            return 1;
        if(str2 == "")
            return -1;
        return ((str1 < str2) ? -1 : ((str1 > str2) ? 1 : 0));
    },

    "title-string-desc": function (str1, str2) {
        if(str1 == "")
            return 1;
        if(str2 == "")
            return -1;
        return ((str1 < str2) ? 1 : ((str1 > str2) ? -1 : 0));
    }
} );
