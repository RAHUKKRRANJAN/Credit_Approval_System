Write-Host "Testing Credit Approval System APIs`n"

# Test 1 Register new customer
Write-Host "1 Testing Register API"
Write-Host "Request POST /api/register/"
$headers = @{ "Content-Type" = "application/json" }
$body = @{
    "first_name" = "Test"
    "last_name" = "User"
    "age" = 30
    "monthly_income" = 50000
    "phone_number" = "9876543001"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/register/" -Method Post -Headers $headers -Body $body
    Write-Host "Response" $response.StatusCode
    Write-Host $response.Content
    Write-Host ""

    $customer = $response.Content | ConvertFrom-Json
    $customerId = $customer.customer_id

    # Test 2 Check eligibility
    Write-Host "2 Testing Check Eligibility API"
    Write-Host "Request POST /api/check-eligibility/"
    $body = @{
        "customer_id" = $customerId
        "loan_amount" = 100000
        "interest_rate" = 16
        "tenure" = 12
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/check-eligibility/" -Method Post -Headers $headers -Body $body
    Write-Host "Response" $response.StatusCode
    Write-Host $response.Content
    Write-Host ""

    # Test 3 Create loan
    Write-Host "3 Testing Create Loan API"
    Write-Host "Request POST /api/create-loan/"
    $body = @{
        "customer_id" = $customerId
        "loan_amount" = 100000
        "interest_rate" = 16
        "tenure" = 12
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/create-loan/" -Method Post -Headers $headers -Body $body
    Write-Host "Response" $response.StatusCode
    Write-Host $response.Content
    Write-Host ""

    # Test 4 View customer loans
    Write-Host "4 Testing View Customer Loans API"
    Write-Host "Request GET /api/view-loans/$customerId"
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/view-loans/$customerId" -Method Get
    Write-Host "Response" $response.StatusCode
    Write-Host $response.Content
    Write-Host ""

    # Test 5 View existing loan
    Write-Host "5 Testing View Loan API"
    Write-Host "Request GET /api/view-loan/5930"
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/view-loan/5930" -Method Get
    Write-Host "Response" $response.StatusCode
    Write-Host $response.Content
    Write-Host ""

    Write-Host "All APIs tested successfully"
}
catch {
    Write-Host "Error occurred:"
    Write-Host $_.Exception.Message
    Write-Host $_.Exception.Response.Content
} 