/*global IoTRPiData _config*/

IoTRPiData.map = IoTRPiData.map || {};

(function iotrpiScope($) {
    let authToken;
    IoTRPiData.authToken.then(function setAuthToken(token) {
        if (token) {
            authToken = token;
        } else {
            window.location.href = '/rpi_signin.html';
        }
    }).catch(function handleTokenError(error) {
        alert(error);
        window.location.href = '/rpi_signin.html';
    });

    function getAllData(date) {
        $.ajax({
            method: 'GET',
            url: _config.api.invokeUrl + '/all/' + date,
            headers: {
                Authorization: authToken
            },
            contentType: 'application/json',
            success: drawGraph,
            error: function ajaxError(jqXHR, textStatus, errorThrown) {
                console.error('Error requesting AWS data: ', textStatus, ', Details: ', errorThrown);
                console.error('Response: ', jqXHR.responseText);
                alert('An error occured when requesting AWS data:\n' + jqXHR.responseText);
            }
        });
    }

    function drawGraph(awsdata) {
        let ctx = document.getElementById("myChart").getContext('2d');
        let items = awsdata.Items;
        let tempData = [];
        let pressData = [];
        let humData = [];
        // process each reading
        for (i = 0; i < awsdata.Count; i++) {
            // process minutes
            minute = parseInt(items[i].calminute.N);
            hours = Math.floor(minute / 60);
            minutes = minute % 60;
            time = '' + hours + ':';
            if (hours < 10) time = '0' + time;
            if (minutes < 10) time = time + '0';
            time = time + minutes;
            // process temperature
            temperature0 = parseFloat(items[i].pitemp0.S);
            pressure0 = parseFloat(items[i].pipress0.S);
            humidity0 = parseFloat(items[i].pihum0.S);
            tempData.push({x: time, y: temperature0})
            pressData.push({x: time, y: pressure0})
            humData.push({x: time, y: humidity0})
        }

        let myChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'Temperature',
                        yAxisID: 'TEMP',
                        fill: false,
                        showLine: true,
                        spanGaps: true,
                        borderColor: 'rgba(255, 0, 0, 1)',
                        borderWidth: 1,
                        pointRadius: 1,
                        data: tempData
                    },
                    {
                        label: 'Pressure',
                        yAxisID: 'PRESS',
                        fill: false,
                        showLine: true,
                        spanGaps: true,
                        borderColor: 'rgba(0, 255, 0, 1)',
                        borderWidth: 1,
                        pointRadius: 1,
                        data: pressData
                    },
                    {
                        label: 'Humidity',
                        yAxisID: 'HUMIDITY',
                        fill: false,
                        showLine: true,
                        spanGaps: true,
                        borderColor: 'rgba(0, 0,255, 1)',
                        borderWidth: 1,
                        pointRadius: 1,
                        data: humData
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            parser: 'hh:mm',
                            unit: 'minute',
                            displayFormats: {
                                day: 'ddd'
                            },
                            min: '00:00:00',
                            max: '23:59:59'
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Time of Day                  '
                        }
                    }],
                    yAxes: [
                        {
                            id: 'TEMP',
                            ticks: {
                            position: 'left',
                                suggestedMin: 0,
                                suggestedMax: 40
                            },
                            scaleLabel: {
                                display: true,
                                labelString: 'Temp Degrees C'
                            }
                        },
                        {
                            id: 'PRESS',
                            position: 'right',
                            ticks: {
                                suggestedMin: 980,
                                suggestedMax: 1020
                            },
                            scaleLabel: {
                                display: true,
                                labelString: 'Press hPa'
                            }
                        },
                        {
                            id: 'HUMIDITY',
                            position: 'left',
                            ticks: {
                                suggestedMin: 40,
                                suggestedMax: 100
                            },
                            scaleLabel: {
                                display: true,
                                labelString: 'Humidity %'
                            }
                        }
                    ]
                },
                legend: {
                    display: true
                },
                animation: {
                    duration: 0,
                },
                hover: {
                    animationDuration: 0,
                },
                responsiveAnimationDuration: 0
            }
        });
    }

    // Register click handler for #request button
    $(function onDocReady() {
        $('#request').submit(handleRequestClick);
        $('#signOut').click(function () {
            IoTRPiData.signOut();
            alert("You have been signed out.");
            window.location = "/rpi_signin.html";
        });

        IoTRPiData.authToken.then(function updateAuthMessage(token) {
            if (token) {
                displayToken(token);
                $('.authToken').text(token);
            }
        });

        if (!_config.api.invokeUrl) {
            $('#noApiMessage').show();
        }
    });

    function handleRequestClick(event) {
        event.preventDefault();
        date = $('#dateInput').val().trim();
        getAllData(date);
    }

    function displayToken(token) {
        let pos = $('#token')
        pos.append($('<li>' + token + '</li>'));
        if (_config.api.invokeUrl) pos.append($('<li>' + _config.api.invokeUrl + '</li>'))
        if (_config.cognito.userPoolId) pos.append($('<li>' + _config.cognito.userPoolId + '</li>'))
        if (_config.cognito.userPoolClientId) pos.append($('<li>' + _config.cognito.userPoolClientId + '</li>'))
        if (_config.cognito.region) pos.append($('<li>' + _config.cognito.region + '</li>'))
    }
}(jQuery));