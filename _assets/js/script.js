/** Epidocs / Past-Exams JS */

$('.embed').click(function(e) {
	e.preventDefault();
	
	var $this = $(this);
	var url = $this.attr('href').replace(/#/g, '%23'); // Encode all '#' characters
	// console.log(url);
	loadPdfEmbed($this.text(), url, $this);
	
	history.pushState({embedUrl: url}, $this.text(), "?" + url.substr(url.lastIndexOf('/') + 1));
	$('#embed').show();
});

$('#embed .embed-close').click(function(e) {
	e.preventDefault();
	history.back();
	$('#embed').hide();
});

window.onpopstate = function(e) {
	$('#embed').hide();
};

function loadPdfEmbed(title, url, $this) {
	url = url || title;
	
	var currPage = 1;
	var numPages;
	var thePDF = null;
	
	$('#embed canvas').remove();
	$('#embed .embed-title .content').text(title);
	$('#embed .embed-title .embed-status').show().find('i').removeClass().addClass('fas fa-spinner fa-pulse fa-fw');
	$('#embed .embed-download').attr('href', url);
	$('#embed .embed-github').attr('href', $this.attr('github-src'));
	$('#embed .embed-error').hide();

	// Asynchronous download of PDF
	var loadingTask = pdfjsLib.getDocument(url);
	loadingTask.promise.then(function(pdf) {
		thePDF = pdf; // pdf object
		numPages = pdf.numPages; // Page count
		
		// Start with first page
		pdf.getPage(currPage).then(handlePages);
	}, function (error) {
		// PDF loading error
		$('#embed .embed-title .embed-status').find('i').removeClass().addClass('fas fa-exclamation-triangle fa-fw');
		$('#embed .embed-error').text('PDF loading error: ' + error).show();
	});
	
	function handlePages(page) {
		console.log('Loading page ' + currPage);
		var canvas = document.createElement( "canvas" );
		canvas.width = 2000; // Large width (same as Github is using)
		
		var viewport = page.getViewport({ scale: canvas.width / page.getViewport({ scale: 1.0 }).width });
		
		var context = canvas.getContext('2d');
		canvas.height = viewport.height;
		canvas.width = viewport.width;

		// Render PDF page into canvas context
		var renderTask = page.render({canvasContext: context, viewport: viewport});

		//Add it to the web page
		document.getElementById('embed').appendChild( canvas );

		// Move to next page
		currPage++;
		if(currPage > numPages)
			$('#embed .embed-title .embed-status').hide();
		else if(thePDF !== null) /* && currPage <= numPages */
			thePDF.getPage(currPage).then(handlePages);
	}
}