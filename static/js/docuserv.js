document.addEventListener("contextmenu", function(e){
    e.preventDefault();
}, false);

$(window).keyup(function(e){
  if(e.keyCode == 44 || e.keyCode == 18){
    $("body").hide();
  }
});

$(window).focus(function() {
  $("body").show();
}).blur(function() {
  $("body").hide();
});

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
        if (y == 0) {
          html += `<a onclick='docView("`;
          html += data_pool[0];
          html +=  `","`;
          html += data_pool[7];
          html += `")' data-toggle="modal" data-target="#modalDoc">`;
          html += data_pool[0];
          html += `</a>`
        }
        else
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


function docView(name, hashpath) {
  $("#modalDocLabel").text(name);
  console.log(hashpath + '-images');
  $.getJSON($SCRIPT_ROOT + '/_file_view', {
    path: hashpath
  }, function(data) {
    imagecnt = data.length;
    html = '';
    for (i = 0; i < imagecnt; i++)
    {
      html += `<image src="data:image/png;base64,`;
      html += data[i];
      html += `" style="width: 95%; height: 95%;"/>`;
    }
    $("#modalDocBod").html(html);
  });
  return false;
}

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
      $("#validate").html(`<form method="post" class="dropzone" id="uploader" action="/_file_upload?type=` + upload + `&quarter=` + quarter + `&year=` + year + `&downloadable=` + downloadable + `&class=` + classcode + `&mf=` + multifile + `">
          <div class="dz-message needsclick">
            Drop file(s) here or click to browse.
          </div>
        </form>
        <div class="progress">
          <div id="uploadProgress" class="progress-bar progress-bar-danger progress-bar-striped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%">
          </div>
        </div>
        <br>
        <div class="row">` + val_inrow + '</div>');
      $("#validate").attr("data-dropzone", "true");
      dz = new Dropzone("#uploader", {
        paramName: "file",
        uploadMultiple: multifile,
        maxFiles: maxfiles,
        autoProcessQueue: false,
        addRemoveLinks: true,
        parallelUploads: maxfiles,
        uploadprogress: function (e, progress) {
          $("#uploadProgress").html(progress + "%");
          $('#uploadProgress').css('width', progress + '%');
        }
      });

      dz.on("addedfile", function(file){
        dz.emit("complete", file);
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
          setTimeout(function() {$("#validate").html(html); update_class_container(classcode)}, 1000);
        });
      }

      else {
        dz.on("success", function(file) {
          setTimeout(function() {$("#validate").html('<h4>Congratulations, you have successfully submitted <br>' + file.name + ' to ' + classcode + '!</h4><br><button class="btn btn-primary btn-block" type="reset" onclick="clearUploadForm()">Close</button>'); update_class_container(classcode)}, 1000);
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

function update_class_container(classcode) {
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
  if (classcode === $("#class").text()) {
    render = classcode.split(' ');
    classRender(render[0], render[1], $("#class_name").text());
  }

  return false;
}

function clearUploadForm() {
  $("#modalUpload").modal('hide');
  setTimeout(function() {
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
    $('#inputErrors').html('')}, 1000);
  return false;
}
