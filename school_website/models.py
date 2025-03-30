class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    # Add other relevant fields

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.student.name}" 