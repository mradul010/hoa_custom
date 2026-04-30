import frappe


def handle_loan_deduction(doc, method):
	# This function calculates total loan deductions for an employee and updates the Salary Slip accordingly.
	doc.flags.ignore_loan_repayment = True

	# Get employee + date
	employee = doc.employee
	end_date = doc.end_date
	total_deduction = 0

	# Fetch loans for employee
	loans = frappe.get_all("Loan", filters={"applicant": employee, "docstatus": 1}, fields=["name"])
	# Loop through repayment schedules
	for loan in loans:
		schedules = frappe.get_all("Loan Repayment Schedule", filters={"loan": loan.name}, fields=["name"])

		for sched in schedules:
			rows = frappe.get_all(
				"Repayment Schedule",
				filters={"parent": sched.name, "payment_date": ["<=", end_date]},
				fields=["principal_amount", "interest_amount"],
			)

			for r in rows:
				total_deduction += (r.principal_amount or 0) + (r.interest_amount or 0)

	# Add / update deduction
	if total_deduction > 0:
		found = False

		for d in doc.deductions:
			if d.salary_component == "Loan Deduction":
				d.amount = total_deduction
				found = True
				break
		if not found:
			doc.append("deductions", {"salary_component": "Loan Deduction", "amount": total_deduction})

	# Recalculate totals
	doc.calculate_net_pay()
