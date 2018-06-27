$(function() {
    $('input[name^=member_]').on('input', function() {
        var $this = $(this)
        var $clone = $this.clone()

        var name = $clone.attr('name')
        var n = parseInt(name.split('_')[1]) + 1
        name = 'member_' + n

        $clone.val('')
        $clone.attr('name', name)
        $clone.appendTo($this.parent())
        // $this.removeClass('interest-list-new')
        $this.off('input', arguments.callee)
        $clone.on('input', arguments.callee)
    })
});


