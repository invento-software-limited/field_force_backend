// Copyright (c) 2022, Invento Software Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Store Visit Assign', {
	refresh: function(frm) {

        // frm.doc.destinations.forEach(function(row) {
        // console.log(row.child_field);
        frm.fields_dict['exp_time'].$wrapper.html(`
           <div class="nativeTimePicker">
            <label for="appt-time">
                Time
            </label>
            <input
              id="appt-time"
              class="form-control"
              type="time"
              name="appt-time"
              required />
          </div>`
        )
        // console.log(frm.fields_dict);
        // console.log("====>>", frm.fields_dict.destinations.layout.fields_dict);
        frm.fields_dict.destinations.layout.fields_dict.exp_time.$wrapper.html(`
           <div class="nativeTimePicker">
            <label for="appt-time">
                Time
            </label>
            <input
              id="appt-time"
              type="time"
              class="form-control"
              name="appt-time"
              required />
          </div>`)

        let div = document.querySelector("[data-fieldname=expected_time][placeholder='Expected Time']");

        // console.log(div.innerHTML='');
        div.innerHTML = `
            <input
              id="appt-time"
              class="form-control"
              type="time"
              name="appt-time"
              required />`;

        // const nativePicker = document.querySelector('.nativeTimePicker');
        // const fallbackPicker = document.querySelector('.fallbackTimePicker');
        // const fallbackLabel = document.querySelector('.fallbackLabel');
        //
        // const hourSelect = document.querySelector('#hour');
        const minuteSelect = document.querySelector('#minute');
        // document.getElementById("appt-time").step = 6;
        //
        let field = document.getElementById("appt-time");
        field.value = frm.doc.exp_time;

        field.addEventListener("change", function(){
            console.log(field.value)
            frappe.model.set_value(frm.doctype, frm.docname, 'exp_time', field.value);
        });
        // // populateMinutes();
        //
        // // Hide fallback initially
        // fallbackPicker.style.display = 'none';
        // fallbackLabel.style.display = 'none';
        //
        // // Test whether a new time input falls back to a text input or not
        // const test = document.createElement('input');
        //
        // try {
        //   test.type = 'time';
        // } catch (e) {
        //   console.log(e.description);
        // }
        //
        // // If it does, run the code inside the if () {} block
        // if (test.type === 'text') {
        //   // Hide the native picker and show the fallback
        //   nativePicker.style.display = 'none';
        //   fallbackPicker.style.display = 'block';
        //   fallbackLabel.style.display = 'block';
        //
        //   // Populate the hours and minutes dynamically
        //   populateHours();
        //   populateMinutes();
        // }
        //
        // function populateHours() {
        //   // Populate the hours <select> with the 6 open hours of the day
        //   for (let i = 12; i <= 18; i++) {
        //     const option = document.createElement('option');
        //     option.textContent = i;
        //     hourSelect.appendChild(option);
        //   }
        // }
        //
        function populateMinutes() {
          // populate the minutes <select> with the 60 hours of each minute
          for (let i = 0; i <= 6; i++) {
            const option = document.createElement('option');
            option.textContent = (i < 60) ? `0${i*10}` : i;
            console.log(option.textContent);
            minuteSelect.appendChild(option);
          }
        }
        //
        // // make it so that if the hour is 18, the minutes value is set to 00
        // // — you can't select times past 18:00
        //  function setMinutesToZero() {
        //    if (hourSelect.value === '18') {
        //      minuteSelect.value = '00';
        //    }
        //  }

         // hourSelect.onchange = setMinutesToZero;
         // minuteSelect.onchange = setMinutesToZero;
    }
});

frappe.ui.form.on('Store Visit Destination', {
	refresh: function(frm, cdt, cdn) {
        frm.fields_dict["destinations"].grid.frm.fields_dict.exp_time.$wrapper.html(`
           <div class="nativeTimePicker">
            <label for="appt-time">
                Time
            </label>
            <input
              id="appt-time"
              class="form-control"
              type="time"
              name="appt-time"
              required />
          </div>`)
    }
});
// <div className="col grid-static-col col-xs-2 " data-fieldname="expected_time" data-fieldtype="Time">
//     <div className="field-area" style="display: none;"></div>
//     <div className="static-area ellipsis">12:11:17</div>
// </div>
// <div className="form-group frappe-control input-max-width" data-fieldtype="Time" data-fieldname="expected_time"
//      title="expected_time"><input type="text" autoComplete="off" className="input-with-feedback form-control input-sm"
//                                   data-fieldtype="Time" data-fieldname="expected_time" placeholder="Expected Time"
//                                   data-doctype="Store Visit Destination" data-col-idx="1"></div>
