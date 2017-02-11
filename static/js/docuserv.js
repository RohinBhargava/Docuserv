document.addEventListener("contextmenu", function(e){
    e.preventDefault();
}, false);

var previousTitle = "Welcome to Docuserv!";
var previousSubtitle = "Rules:";
var homeHTML = $("#table_update").html();
var dateObj = new Date();
var startTime = dateObj.getTime();
var imgDim;
var startPage;
var endPage;
var hp;
var circles = `<div class="cssload-wrap">
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
  <div class="cssload-circle"></div>
</div>`;

$(window).keydown(function(e){
  if(e.keyCode == 44 || e.keyCode == 18){
    $("body").hide();
  }

  if (e.keyCode == 187 && e.ctrlKey && ($("#modalDoc").data('bs.modal') || {}).isShown)
  {
    e.preventDefault();
    imgDim = imgDim + 2;
    if (imgDim > 95)
    {
      imgDim = 95;
    }
    changeImgCss();
  }

  if (e.keyCode == 189 && e.ctrlKey && ($("#modalDoc").data('bs.modal') || {}).isShown)
  {
    e.preventDefault();
    if (imgDim < 0)
    {
      imgDim = 0;
    }
    imgDim = imgDim - 2;
    changeImgCss();
  }

  if (e.keyCode == 83 && e.ctrlKey)
    e.preventDefault();
});

$(window).keyup(function(e){
  if(e.keyCode == 44 || e.keyCode == 18){
    $("body").show();
  }
});

$(window).on('mousewheel wheel', function(event)
{
    if(event.ctrlKey == true && ($("#modalDoc").data('bs.modal') || {}).isShown)
    {
        event.preventDefault();
        if(event.originalEvent.deltaY > 0) {
          imgDim = imgDim - 2;
          if (imgDim < 0)
          {
            imgDim = 0;
          }
          changeImgCss();
        }
        else {
          imgDim = imgDim + 2;
          if (imgDim > 95)
          {
            imgDim = 95;
          }
          changeImgCss();
        }
    }
});

function changeImgCss() {
  $(".doc").css("width",  imgDim + "%");
  $(".doc").css("height", imgDim + "%");
}

$(document).on('click', function(e) {
  $('[data-toggle="popover"],[data-original-title]').each(function() {
    if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
      $(this).popover('hide').data('bs.popover').inState.click = false
    }
  });
});

$("#search").keyup(function() {
  var query = $("#search").val();
  dateObj = new Date();

  if (query === "") {
    resetSearch();
  }

  else if (dateObj.getTime() - startTime > 100) {
    $("#searchReset").show();
    $("#search").css("padding-right", "24px");
    $.getJSON($SCRIPT_ROOT + '/_search_all', {
      term: query
    }, function(response) {
        if ($("#class").text() !== "Docuserv Search")
        {
          previousTitle = $("#class").text();
          previousSubtitle = $("#class_name").text();
        }
        $("#class").text("Docuserv Search");
        $("#class_name").text(query);
        tableList(response, '', '', true);
    });
    startTime = dateObj.getTime();
  }
});

function resetSearch() {
  $('#searchReset').hide();
  $("#search").css("padding-right", "12px");

  if (previousTitle === "Welcome to Docuserv!") {
    $("#class").text(previousTitle);
    $("#class_name").text(previousSubtitle);
    $("#table_update").html(homeHTML);
  }

  else {
    render = previousTitle.split(' ');
    classRender(render[0], render[1], previousSubtitle);
  }

  $("#search").val("");
  return false;
}

function classRender(i, j, k) {
  $.getJSON($SCRIPT_ROOT + '/_get_class', {
    code: i,
    num: j
  }, function(data) {
    $("#class").text(i + " " + j);
    $("#class_name").text(k);
    tableList(data, i , j, false);
  });

  return false;
}

function tableList(data, i, j, glo) {
  var i_copy = i;
  var j_copy = j;
  var html = `<table id="file_table" class="table table-striped">
    <thead>
      <tr>
        <th><span class="glyphicon glyphicon-eye-open pull-left" aria-hidden="true"></span> Name</th>
        <th><span class="glyphicon glyphicon-floppy-disk pull-left" aria-hidden="true"></span> Extension</th>
        <th><span class="glyphicon glyphicon-tag pull-left" aria-hidden="true"></span> Quarter</th>
        <th><span class="glyphicon glyphicon-calendar pull-left" aria-hidden="true"></span> Year</th>
        <th><span class="glyphicon glyphicon-cloud-download pull-left" aria-hidden="true"></span> Downloadable</th>
        <th><span class="glyphicon glyphicon-hdd pull-left" aria-hidden="true"></span> Size</th>
        <th><span class="glyphicon glyphicon-paperclip pull-left" aria-hidden="true"></span> Upload Type</th>
        <th><span class="glyphicon glyphicon-man pull-left" aria-hidden="true"></span> Teacher</th>`
        if (glo)
        {
          html += `<th><span class="glyphicon glyphicon-book pull-left" aria-hidden="true"></span> Class</th>`
        }
      html +=  `<th></th>
      </tr>
            </thead>
            <tbody>`;
  var info = data["info"];

  if (info.length === 0 && !glo) {
    previousTitle = "Welcome to Docuserv!";
    previousSubtitle = "Rules:";
    resetSearch();
    return false;
  }

  for (z = 0; z < info.length; z++)
  {
    var data_pool = info[z];
    console.log(data_pool);
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
      else if (y == 4 && data_pool[4] == 'Yes') {
        html += `<a href="/_file_serve?file=`;
        html += data_pool[7];
        html += '&name=';
        html += data_pool[0];
        html += '&extension=';
        html += data_pool[1];
        html += `">`;
        html += data_pool[4];
        html += "</a>";
      }
      else
        html += data_pool[y];
      html += `</td>\n`;
    }

    if (glo)
    {
      html += `<td>`;
      html += data_pool[9];
      html += `</td>`;
      var splitted = data_pool[9].split(' ');
      i_copy = splitted[0];
      j_copy = splitted[1];
    }

    html += `<td>`;
    if (data_pool[8])
    {
      html += `<a data-toggle="popover" data-placement="left" data-content="Are you sure you want to delete this? The file will be deleted forever. <br><button class='btn btn-danger btn3d' onclick='deleteFile(`;
      html += `\``;
      html += i_copy;
      html+= `\``;
      html += ', ';
      html += `\``;
      html += j_copy;
      html += `\``;
      html += ', ';
      html += `\``;
      html += data_pool[7];
      html += `\``;
      html += `)' align='center'>Delete!</button>"><span class="glyphicon glyphicon-remove delete" aria-hidden="true"></span></a>`;
    }
    html += `</td>`;
    html += `\t</tr>\n`;
  }
  html += `</tbody>
  </table>`;
  $("#table_update").html(html);
  $("[data-toggle=\"popover\"]").popover({
    "animation": true,
    "html": true
  });

  if (glo) {
    $('#file_table').DataTable({
        "iDisplayLength": 25,
        "columnDefs": [ { orderable: false, targets: 8 }, { type: 'file-size', targets: 5 }, { type: 'title-string', targets: 7} ],
        "order": []
    });
  }

  else {
    $('#file_table').DataTable({
        "iDisplayLength": 25,
        "columnDefs": [ { orderable: false, targets: 7 }, { type: 'file-size', targets: 5 } ]
    });
  }

  return false;
}

$('.collapse').on('show.bs.collapse', function (e) {
  $("#" + e.currentTarget.id.substring(8,13)).attr("data-focused", "true");
});
$('.collapse').on('hide.bs.collapse', function (e) {
  $("#" + e.currentTarget.id.substring(8,13)).attr("data-focused", "false");
});

function imageRender(data) {
  imagecnt = data.length;
  html = '';
  for (i = 0; i < imagecnt; i++)
  {
    html += `<img class="doc" src="data:image/png;base64,`;
    html += data[i];
    html += `" draggable="false" ondragstart="return false;"/>`;
  }
  if (imagecnt === 0)
    html = `Nothing to show here. If you have just uploaded this file, it may take some time to process. If you think this is an error, contact the system administrator.`

  html += `<div id="docButtons"></div>`
  return html;
}

function docPrevious() {
  $("#modalDocBod").html(circles);
  $.getJSON($SCRIPT_ROOT + '/_file_view_previous', {
    path: hp,
    page: startPage
  },
  function(data) {
    if (data[0].length == 0)
      return false;
    $("#modalDocBod").html(imageRender(data[0]) + `
    <div id="#pageForm" onKeyPress="checkSubmit(event)">
      <input id="pagev" type="text" value="` + data[1] + `">
    </div>`);
    changeImgCss();
    endPage = startPage;
    startPage = data[1];
  });
  return false;
}

function docNext() {
  $("#modalDocBod").html(circles);
  $.getJSON($SCRIPT_ROOT + '/_file_view_next', {
    path: hp,
    page: endPage
  },
  function(data) {
    if (data[0].length == 0)
      return false;
    $("#modalDocBod").html(imageRender(data[0]) + `
    <div id="#pageForm" onKeyPress="checkSubmit(event)">
      <input id="pagev" type="text" value="` + endPage + `">
    </div>`);
    changeImgCss();
    startPage = endPage;
    endPage = data[1];
  });
  return false;
}

function docView(name, hashpath) {
  $("#modalDocLabel").html(`<span class="glyphicon glyphicon-menu-left" onclick="docPrevious()"></span>` + name + `<span class="glyphicon glyphicon-menu-right" onclick="docNext()"></span>`);
  $("#modalDocBod").html(circles);
  $.getJSON($SCRIPT_ROOT + '/_file_view', {
    path: hashpath,
    page: 0
  }, function(data) {
    $("#modalDocBod").html(imageRender(data) + `
    <div id="#pageForm" onKeyPress="checkSubmit(event)">
      <input id="pagev" type="text" value="0">
    </div>`);
    hp = hashpath;
    imgDim = 95;
    startPage = 0;
    endPage = data.length;
  });

  return false;
}

function getPage(ppage) {
  $("#modalDocBod").html(circles);
  $.getJSON($SCRIPT_ROOT + '/_file_view_next', {
    path: hp,
    page: ppage
  },
  function(data) {
    if (data[0].length == 0)
      return false;
    $("#modalDocBod").html(imageRender(data[0]) + `
    <div id="#pageForm" onKeyPress="checkSubmit(event)">
      <input id="pagev" type="text" value="` + ppage + `">
    </div>`);
    changeImgCss();
    startPage = ppage;
    endPage = data[1];
  });
  return false;
}

function checkSubmit(e) {
  console.log(e.keyCode);
   if(e && e.keyCode == 13) {
      getPage($("#pagev").val());
   }
   return false;
}

function alertContent(sucorerr, mes) {
  $("#modalAlertLabel").text(sucorerr);
  $("#modalAlertBod").html(mes);
  return false;
}

var dz;
var val_html = $("#validate").html();

function validateMeta() {
  var val_inrow = $("#inputRow").html();
  var upload = $("#inputUpload").val();
  var quarter = $("#inputQuarter").val();
  var year = $("#inputYear").val();
  var downloadable = $("#inputDownloadable").val();
  var classcode = $("#inputClass").val();
  var teacher = $("#inputTeacher").val();
  if ($("#inputMF:checked").val() === "on") {
    var multifile = true;
    var maxfiles = 15;
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
      $("#validate").html(`<form method="post" class="dropzone" id="uploader" action="/_file_upload?type=` + upload + `&quarter=` + quarter + `&year=` + year + `&downloadable=` + downloadable + `&class=` + classcode + `&teacher` + teacher + `&mf=` + multifile + `">
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
          html += '<br><button class="btn btn-danger btn3d" type="reset" onclick="clearUploadForm()">Close</button>';
          setTimeout(function() {$("#validate").html(html); updateClassContainer(classcode)}, 1000);
        });
      }

      else {
        dz.on("success", function(file) {
          setTimeout(function() {$("#validate").html('<h4>Congratulations, you have successfully submitted <br>' + file.name + ' to ' + classcode + '!</h4><br><button class="btn btn-danger btn3d" type="reset" onclick="clearUploadForm()">Close</button>'); updateClassContainer(classcode)}, 1000);
        });
      }

      dz.on("error", function(file) {
        dz.removeFile(file);
      });

      $("#upload-button").html("<span class='glyphicon glyphicon-cloud-upload pull-left' aria-hidden='true'></span> Submit");
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

function updateClassContainer(classcode) {
  $.getJSON($SCRIPT_ROOT + "/_class_container_update",
    function(data) {
      var classContainer = data["class_container"];
      var html = "";
      var classnum = false;
      var render = classcode.split(' ');
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
          if (classTuple[0] === render[1])
            classnum = true;
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

      if (!classnum)
      {
        $("#class").text("Welcome to Docuserv!");
        $("#class_name").text("Rules:");
        $("#table_update").html(homeHTML);
      }

      else if (classcode === $("#class").text()) {
        classRender(render[0], render[1], $("#class_name").text());
      }
  });

  return false;
}

function clearUploadForm() {
  $("#modalUpload").modal('toggle');
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

function deleteFile(i, j, hashpath) {
  $.ajax ({
      url: $SCRIPT_ROOT + "/_del_file",
      data: {
          code: i,
          num: j,
          hashpath: hashpath
      }
    }).done(function(response) {
      if (response === "DELETED")
        updateClassContainer(i + " " + j)
  });
  return false;
}
