# Django Datatables server processing
Django class for full Datatables server processing implementation

https://datatables.net/examples/data_sources/server_side.html

After hanging around for a good integration of Datatables server processing in Django, I tested the things I found on internet but they all have the same problem, they cannot manage the ForeignKey relations as well. 
After all, I made it by myself.

This code was tested on Datatables 1.10.+ and Django 1.10.+.

To get it works just put datatables in your html template, like this:

```html
    <!-- jQuery -->
    <script src="/statics/js/vendors/jquery/dist/jquery.min.js"></script>
    <!-- Datatables -->
    <script src="/statics/js/vendors/datatables.net/js/jquery.dataTables.js"></script>
    
    <!-- Datatables -->
    <script>
      $(document).ready(function() {

        $('.datatable-responsive-serverside').DataTable({
        
            "aLengthMenu": [
            [25, 50, 100, 500, ], // -1],
            [25, 50, 100, 500, ] //"All"]
            ],
            "paging": true,
            "responsive": true,
            "processing": true,
            "serverSide": true,
            "ajax": "{% url 'appnamespace:viewname_json' %}",
            //~ "ajax": {
                  //~ url: "{% url 'appnamespace:viewname_json' %",
                  //~ method: 'post',
                  //~ data: function(args) {
                    //~ return {
                      //~ "args": JSON.stringify(args)
                    //~ };
                  //~ }
                //~ },
        });
        
    });
    </script>
```
