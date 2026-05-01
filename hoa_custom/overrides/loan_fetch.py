import frappe


def handle_loan_deduction(doc, method):
	employee = doc.employee
	total_deduction = 0

	clean_deductions = []
	for d in doc.deductions:
		if "loan" not in (d.salary_component or "").lower():
			clean_deductions.append(d)

	doc.deductions = clean_deductions

	# Fetch ONLY this month EMI
	processed_rows = set()

	loans = frappe.get_all("Loan", filters={"applicant": employee, "docstatus": 1}, fields=["name"])

	for loan in loans:
		schedules = frappe.get_all("Loan Repayment Schedule", filters={"loan": loan.name}, fields=["name"])

		for sched in schedules:
			rows = frappe.get_all(
				"Repayment Schedule",
				filters={"parent": sched.name, "payment_date": ["between", [doc.start_date, doc.end_date]]},
				fields=["name", "principal_amount", "interest_amount"],
			)

			for r in rows:
				if r.name in processed_rows:
					continue

				processed_rows.add(r.name)

				total_deduction += (r.principal_amount or 0) + (r.interest_amount or 0)

	if total_deduction > 0:
		doc.append("deductions", {"salary_component": "Loan Deduction", "amount": total_deduction})

	doc.total_deduction = sum(d.amount for d in doc.deductions)
	doc.net_pay = doc.gross_pay - doc.total_deduction
	doc.rounded_total = round(doc.net_pay, 2)
