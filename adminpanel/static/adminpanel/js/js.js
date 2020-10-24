$(document).ready(function () {
    $("#checkAll").on("click", function () {
        if (!this.checked) {
            $("td input[type=checkbox]").prop("checked", false)
            $("td input[type=checkbox]").attr("disabled", false)
        }
        if (this.checked) {
            $("td input[type=checkbox]").prop("checked", true)
            $("td input[type=checkbox]").attr("disabled", true)

        }
    })
    $("#do-collection-archive").on("click", function (e) {
        e.preventDefault()
        const action = $("#collection-selector").val()
        if (action == "null") {
            return false
        } else {
            const selected = $("td input[type=checkbox]:checked")
            console.log(selected.length)
            if(selected.length === 0){
                return false
            }
            let data = {}
            $.each(selected, function (i, v) {
                const val = $(v).val().split('-')
                data[i] = {"id" : val[1]}
            })
            $.ajaxSetup({
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "contentType": 'application/json',
            }
        });
        e.preventDefault()
        const showingItems = $("#showingItems")
        const sitestatus = $("#sitestatus")
        const tradition1 = $("#tradition1")
        const tradition2 = $("#tradition2")
        const body = {
            handler: 'deleteArchives',
            data : JSON.stringify(data) ,
            csrftoken: getCookie("csrftoken")
        }
        $.ajax("http://localhost:8000/adminpanel/postHandler", {
            method: 'POST',
            data: body,
        }).then(resp => {
            if (resp.code === 200) {
                $.notify(resp.counter + " تغییر با موفقیت اعمال شد", {
                    position: "top center",
                    style: "bootstrap",
                    className: "success",
                    autoHideDelay: 4000,
                    gap: 2
                })
                location.reload()
            } else {
                console.log(resp)
                $.notify("تغییرات با موفقیت اعمال نشد !", {
                    position: "top center",
                    style: "bootstrap",
                    className: "error",
                    autoHideDelay: 4000,
                    gap: 2

                })
            }
        }).catch(err => {
            $.notify("تغییرات با موفقیت اعمال نشد !", {
                position: "top center",
                style: "bootstrap",
                className: "error",
                autoHideDelay: 4000,
                gap: 2

            })
            console.log(err)
        })
        }
    })
    $("#do-collection-conductor").on("click", function (e) {
        e.preventDefault()
        const action = $("#collection-selector").val()
        if (action == "null") {
            return false
        } else {
            const selected = $("td input[type=checkbox]:checked")
            console.log(selected.length)
            if(selected.length === 0){
                return false
            }
            let data = {}
            $.each(selected, function (i, v) {
                const val = $(v).val().split('-')
                data[i] = {"id" : val[1]}
            })
            $.ajaxSetup({
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "contentType": 'application/json',
            }
        });
        e.preventDefault()
        const showingItems = $("#showingItems")
        const sitestatus = $("#sitestatus")
        const tradition1 = $("#tradition1")
        const tradition2 = $("#tradition2")
        const body = {
            handler: 'deleteConductor',
            data : JSON.stringify(data) ,
            csrftoken: getCookie("csrftoken")
        }
        $.ajax("http://localhost:8000/adminpanel/postHandler", {
            method: 'POST',
            data: body,
        }).then(resp => {
            if (resp.code === 200) {
                $.notify(resp.counter + " تغییر با موفقیت اعمال شد", {
                    position: "top center",
                    style: "bootstrap",
                    className: "success",
                    autoHideDelay: 4000,
                    gap: 2
                })
                location.reload()
            } else {
                console.log(resp)
                $.notify("تغییرات با موفقیت اعمال نشد !", {
                    position: "top center",
                    style: "bootstrap",
                    className: "error",
                    autoHideDelay: 4000,
                    gap: 2

                })
            }
        }).catch(err => {
            $.notify("تغییرات با موفقیت اعمال نشد !", {
                position: "top center",
                style: "bootstrap",
                className: "error",
                autoHideDelay: 4000,
                gap: 2

            })
            console.log(err)
        })
        }
    })

    var date = new Date()
    $("#time").html(date.toLocaleString("fa", {}))

    $(".eye-button").hover(function () {
        $("svg.fa-eye-slash").css("display", "none")
        $("svg.fa-eye").css("display", "block")
        $(".login-container #password").attr("type", "text")
    }, function () {
        $("svg.fa-eye").css("display", "none")
        $("svg.fa-eye-slash").css("display", "block")
        $(".login-container #password").attr("type", "password")
    })

    $(".login-container #submit").on("click", function (e) {
        e.preventDefault()
        $(".login-container #submit").attr("disabled", "true")
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "contentType": 'application/json',
            }
        });
        e.preventDefault()
        const username = $("#username").val()
        const address = $("form").attr("action")
        console.log(address)
        const password = $("#password").val()
        const data = {
            handler: 'login',
            username: username,
            password: password,
            csrftoken: $("input[name='csrfmiddlewaretoken']").val()
        }
        $.ajax(address, {
            method: 'POST',
            data: data,
        }).then(resp => {
            if (resp.code === 200) {
                $.notify("شما با موفقیت وارد شدید", {
                    position: "top center",
                    style: "bootstrap",
                    className: "success",
                    autoHideDelay: 4000,
                    gap: 2
                })
                setTimeout(function () {
                    location.reload();
                }, 1000)
            } else {
                $(".login-container #submit").removeAttr("disabled")
                console.log(resp)
                $.notify("ورود موفقیت آمیز نبود", {
                    position: "top center",
                    style: "bootstrap",
                    className: "error",
                    autoHideDelay: 4000,
                    gap: 2

                })
            }
        }).catch(err => {
            $(".login-container #submit").removeAttr("disabled")
            $.notify("ورود موفقیت آمیز نبود", {
                position: "top center",
                style: "bootstrap",
                className: "error",
                autoHideDelay: 4000,
                gap: 2

            })
            console.log(err)
        })


    })

    setInterval(function () {
        var date = new Date()
        $("#time").html(date.toLocaleString("fa"))
    }, 1000)

    $("#set-settings").on("click", function (e) {
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "contentType": 'application/json',
            }
        });
        e.preventDefault()
        const showingItems = $("#showingItems")
        const sitestatus = $("#sitestatus")
        const tradition1 = $("#tradition1")
        const tradition2 = $("#tradition2")
        const data = {
            handler: 'setSettings',
            showingItems: showingItems.val(),
            sitestatus: sitestatus.val(),
            tradition1: tradition1.val(),
            tradition2: tradition2.val(),
            csrftoken: getCookie("csrftoken")
        }
        $.ajax("http://localhost:8000/adminpanel/postHandler", {
            method: 'POST',
            data: data,
        }).then(resp => {
            if (resp.code === 200) {
                $.notify(resp.counter + " تغییر با موفقیت اعمال شد", {
                    position: "top center",
                    style: "bootstrap",
                    className: "success",
                    autoHideDelay: 4000,
                    gap: 2
                })
            } else {
                console.log(resp)
                $.notify("تغییرات با موفقیت اعمال نشد !", {
                    position: "top center",
                    style: "bootstrap",
                    className: "error",
                    autoHideDelay: 4000,
                    gap: 2

                })
            }
        }).catch(err => {
            $.notify("تغییرات با موفقیت اعمال نشد !", {
                position: "top center",
                style: "bootstrap",
                className: "error",
                autoHideDelay: 4000,
                gap: 2

            })
            console.log(err)
        })
    })
})

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}