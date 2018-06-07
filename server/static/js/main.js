$(document).ready(function () {
	const hold = $('#main');
	$('#top').on('click', function (e) {
		e.preventDefault()
		$.ajax({
			url: "/api/top.json",
			data: 'json',
			success: function (result) {
				console.log(result);
				hold.empty();
				let table = `<div class="title"><strong>TOP</strong></div><table class="table">
<thead><th></th><th>Name</th><th>Grade</th></thead>`;
				let topList = result['top'].forEach(function (e, i) {
					table += `<tr><td>${i + 1}</td><td>${e.teacher_short_name}</td><td>${e.avg_mark}</td></tr>`
				});
				table += `</table>`;
				let topWrapper = $('<div class="topWrapper"></div>')
				topWrapper.html(table);
				hold.html(topWrapper);
			}
		});
	})
	$('#index').on('click', function (e) {
		e.preventDefault()
		hold.html(`<div class=" d-flex main-wrapper">
            <form class="form-inline my-2 my-lg-0">
                <input class="form-control mr-sm-2" type="search" placeholder="Your teacher surname" aria-label="Search">
                <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
            </form>
    </div>`);
	})
});