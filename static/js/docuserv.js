// var last_focus = "none";

function pausecomp(millis) {
  var date = new Date();
  var curDate = null;
  do { curDate = new Date(); }
  while(curDate-date < millis);
}

function classRender(i, j, k) {
  $.getJSON($SCRIPT_ROOT + '/_get_class', {
    code: i,
    num: j
  }, function(data) {
    $("#class").text(i + " " + j);
    $("#class_name").text(k);
    $("#class_name").attr("type", "text");
    $("#class_name").attr("class", "sub-header");
    // $("#" + i + j).attr("data-focused", "true");
    // if (last_focus != "none" && last_focus != i + j)
    // {
    //   $("#" + last_focus).attr("data-focused", "false");
    // }
    // last_focus = i + j;
    var html = `<table class="table table-striped">
      <thead>
        <tr>
          <th>Name</th>
          <th>Extension</th>
          <th>Quarter</th>
          <th>Year</th>
          <th>Downloadable</th>
          <th>Size</th>
          <th>Upload Type</th>
        </tr>
      </thead>
      <tbody>`;
    var info = data["info"];
    for (z = 0; z < info.length; z++)
    {
      var data_pool = info[z];
      html += `\n\t<tr>\n`;
      for (y = 0; y < 7; y++)
      {
        html += `\t\t<td>`;
        html += data_pool[y];
        html += `</td>\n`;
      }
      html += `\t</tr>\n`;
    }
    html += `</tbody>
    </table>`;
    $("#table_update").html(html);
  });
  return false;
}
$('.collapse').on('show.bs.collapse', function (e) {
  $("#" + e.currentTarget.id.substring(8,13)).attr("data-focused", "true");
});
$('.collapse').on('hide.bs.collapse', function (e) {
  $("#" + e.currentTarget.id.substring(8,13)).attr("data-focused", "false");
});

var dz;
var val_html = $("#validate").html();

function validateMeta() {
  var val_inrow = $("#inputRow").html();
  var upload = $("#inputUpload").val()
  var quarter = $("#inputQuarter").val()
  var year = $("#inputYear").val()
  var downloadable = $("#inputDownloadable").val()
  var classcode = $("#inputClass").val()
  if ($("#inputMF:checked").val() === "on") {
    var multifile = true;
    var maxfiles = 100;
  }
  else {
    var multifile = false;
    var maxfiles = 1;
  }

  $.getJSON($SCRIPT_ROOT + "/_validate", {
    upload: upload,
    quarter: quarter,
    year: year,
    downloadable: downloadable,
    class: classcode
  }, function(data) {
    var errors = data["error"];
    if (errors.length === 0) {
      $("#inputErrors").html('');
      $("#validate").html(`<form method="post" class="dropzone" id="uploader" action="/_file_upload?type=` + upload + `&quarter=` + quarter + `&year=` + year + `&downloadable=` + downloadable + `&class=` + classcode + `">
          <div class="dz-message needsclick">
            Drop file here or click to browse.
          </div>
        </form>
        <br>
        <div class="row">` + val_inrow + '</div>');
      $("#validate").attr("data-dropzone", "true");
      dz = new Dropzone("#uploader", {
        paramName: "file",
        uploadMultiple: multifile,
        maxFiles: maxfiles,
        autoProcessQueue: false,
        addRemoveLinks: true,
        parallelUploads: maxfiles
      });

      if (multifile) {
        dz.on("successmultiple", function(file) {
          var html = '<h4>Congratulations, you have successfully submitted <br> the following files to ' + classcode + ':</h4>';
          for (i = 0; i < file.length; i++)
          {
            html += file[i].name;
            html += "<br>"
          }
          html += '<br><button class="btn btn-primary btn-block" type="reset" onclick="clearUploadForm()">Close</button>';
          $("#validate").html(html);
        });
      }

      else {
        dz.on("success", function(file) {
          $("#validate").html('<h4>Congratulations, you have successfully submitted <br>' + file.name + ' to ' + classcode + '!</h4><br><button class="btn btn-primary btn-block" type="reset" onclick="clearUploadForm()">Close</button>');
        });
      }

      dz.on("error", function(file) {
        dz.removeFile(file);
      });

      $("#upload-button").text("Submit");
      $("#upload-button").attr("onclick", "dz.processQueue()");
    }
    else {
      var html = "";
      for (i = 0; i < errors.length; i++)
      {
        html += "<br>";
        html += errors[i];
      }
      $("#inputErrors").html(html);
    }
  });

  return false;
}

function clearUploadForm() {
  $.getJSON($SCRIPT_ROOT + "/_class_container_update",
    function(data) {
      var classContainer = data["class_container"];
      var html = "";
      for (var iteri in classContainer) {
        html += '<li>'
        if (!$("#" + iteri).length) {
          html += '<a data-toggle="collapse" href="#collapse';
          html += iteri;
          html += '" data-focused="false" id="';
          html += iteri;
          html += '">';
          html += iteri;
          html += '</a></li><div id="collapse';
          html += iteri;
          html += '" class="collapse">';
        }
        else {
          html += $("#" + iteri)[0].outerHTML;
          html += '</li>';
          html += $("#collapse" + iteri)[0].outerHTML.split(">")[0];
          html += ">";
        }
        html += '<ul class="nav">';
        var iterj = classContainer[iteri];
        for (j = 0; j < iterj.length; j++) {
          var classTuple = iterj[j];
          html += '<li><a onclick="classRender(\'';
          html += iteri;
          html += '\', \'';
          html += classTuple[0];
          html += '\', \'';
          html += classTuple[1];
          html += '\');">';
          html += classTuple[0];
          html += '</a></li>';
        }
        html += '</ul></div><br>';
      }
      $("#classContainer").html(html);
      $('.collapse').on('show.bs.collapse', function (e) {
        $("#" + e.currentTarget.id.substring(8,13)).attr("data-focused", "true");
      });
      $('.collapse').on('hide.bs.collapse', function (e) {
        $("#" + e.currentTarget.id.substring(8,13)).attr("data-focused", "false");
      });
  });

  // $.getJSON($SCRIPT_ROOT + "/_class_container_update", function(data) {
  //   console.log($("#classContainer li")[0]);
  //   var classContainer = data["class_container"];
  //   var pos = 0;
  //   var containerLength = $('#classContainer li').length;
  //   for (var iteri in classContainer) {
  //     if (pos === containerLength)
  //     {
  //       var i = classContainer[iteri]
  //       var j0 = i[0][0];
  //       var j1 = i[0][1];
  //       // $("#classContainer").
  //       break;
  //     }
  //     if (!$("#" + iteri).length)
  //       console.log(iteri);
  //     pos += 1;
  //   }
  // });
  $("#modalUpload").modal('hide');
  if ($("#validate").attr("data-dropzone") === "true") {
    $("#upload-button").text("Validate");
    $("#validate").html(val_html);
  }

  else {
    $(".form-control").each(function() {
      $(this).val('');
    });
  }

  $("#validate").attr("data-dropzone", "false");
  $('#inputErrors').html('');
  return false;
}

function fileUpload() {
  console.log($("#uploader").html());
}
