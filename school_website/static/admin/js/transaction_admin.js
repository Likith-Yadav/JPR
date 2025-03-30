(function($) {
    $(document).ready(function() {
        // Add current date/time button
        var dateField = $('input[name="date"]');
        var timeField = $('input[name="time"]');
        
        if (dateField.length && timeField.length) {
            var currentDateTimeButton = $('<button>')
                .attr('type', 'button')
                .addClass('button')
                .text('Set Current Date & Time')
                .css('margin-left', '10px')
                .click(function() {
                    var now = new Date();
                    var dateStr = now.toISOString().split('T')[0];
                    var timeStr = now.toTimeString().slice(0, 5);
                    
                    dateField.val(dateStr);
                    timeField.val(timeStr);
                });
            
            dateField.after(currentDateTimeButton);
        }
    });
})(django.jQuery); 