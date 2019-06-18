var dragHandler = function(evt){
    evt.preventDefault();
};


var dropHandlerTrans = function(evt){
  evt.preventDefault();
  var files = evt.originalEvent.dataTransfer.files;

  var formData = new FormData();
  formData.append("xmlfile", files[0]);

  var req = {
      url: "/convert_transactions",
      method: "post",
      processData: false,
      contentType: false,
      data: formData,
      success: function(response, status, xhr) {
          // check for a filename
          var filename = "";
          var disposition = xhr.getResponseHeader('Content-Disposition');
          if (disposition && disposition.indexOf('attachment') !== -1) {
              var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
              var matches = filenameRegex.exec(disposition);
              if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
          }

          var type = xhr.getResponseHeader('Content-Type');
          var blob = new Blob([response], { type: type });

          if (typeof window.navigator.msSaveBlob !== 'undefined') {
              // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
              window.navigator.msSaveBlob(blob, filename);
          } else {
              var URL = window.URL || window.webkitURL;
              var downloadUrl = URL.createObjectURL(blob);

              if (filename) {
                  // use HTML5 a[download] attribute to specify filename
                  var a = document.createElement("a");
                  // safari doesn't support this yet
                  if (typeof a.download === 'undefined') {
                      window.location = downloadUrl;
                  } else {
                      a.href = downloadUrl;
                      a.download = filename;
                      document.body.appendChild(a);
                      a.click();
                  }
              } else {
                  window.location = downloadUrl;
              }

              setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup
          }
      }
  };

  $.ajax(req);
};

var dropHandlerBudgets = function(evt){
  evt.preventDefault();
  var files = evt.originalEvent.dataTransfer.files;

  var formData = new FormData();
  formData.append("xmlfile", files[0]);

  var req = {
      url: "/convert_budgets",
      method: "post",
      processData: false,
      contentType: false,
      data: formData,
      success: function(response, status, xhr) {
          // check for a filename
          var filename = "";
          var disposition = xhr.getResponseHeader('Content-Disposition');
          if (disposition && disposition.indexOf('attachment') !== -1) {
              var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
              var matches = filenameRegex.exec(disposition);
              if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
          }

          var type = xhr.getResponseHeader('Content-Type');
          var blob = new Blob([response], { type: type });

          if (typeof window.navigator.msSaveBlob !== 'undefined') {
              // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
              window.navigator.msSaveBlob(blob, filename);
          } else {
              var URL = window.URL || window.webkitURL;
              var downloadUrl = URL.createObjectURL(blob);

              if (filename) {
                  // use HTML5 a[download] attribute to specify filename
                  var a = document.createElement("a");
                  // safari doesn't support this yet
                  if (typeof a.download === 'undefined') {
                      window.location = downloadUrl;
                  } else {
                      a.href = downloadUrl;
                      a.download = filename;
                      document.body.appendChild(a);
                      a.click();
                  }
              } else {
                  window.location = downloadUrl;
              }

              setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup
          }
      }
  };

  $.ajax(req);
};

var dropHandlerSet1 = {
    dragover: dragHandler,
    drop: dropHandlerTrans
};
var dropHandlerSet2 = {
    drop: dropHandlerBudgets
};

$(".container-full").on(dropHandlerSet1);
$(".container-full").on(dropHandlerSet2);
