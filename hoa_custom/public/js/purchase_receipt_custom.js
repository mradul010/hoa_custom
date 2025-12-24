frappe.ui.form.on('Purchase Receipt Item', {
    rejected_qty(frm,cdt,cdn){
        const row = locals[cdt][cdn];
        const qty = flt(row.qty || 0);
        const rejected = flt(row.rejected_qty || 0);

        if (rejected > 0){
            const balance = qty - rejected;
            frappe.model.set_value(cdt, cdn, 'balance_quantity', balance);
        } else{
            frappe.model.set_value(cdt, cdn, 'balance_quantity', 0);
        }
    }
});