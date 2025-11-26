# Stock Predictor - Quick Start Guide

## 🔐 Access Control

### Free Features (No Login)
- ✅ View Top 20 Nifty 200 Stocks
- ✅ See Trading Predictions (Buy/Sell/Hold)
- ✅ View Technical Indicators (RSI, SMA, ATR, MACD)
- ✅ Use Stock Search and Filters
- ✅ Basic Chart Visualization

### Premium Features (Login Required)
- 🔒 Quick Stock Analysis
- 🔒 Market Insights & Analysis
- 🔒 Analysis Summary
- 🔒 Export to CSV
- 🔒 Advanced Charts

## 🔑 Login Instructions

**Demo Credentials:**
- Username: `admin`
- Password: `password`

**How to Login:**
1. Click the "Login" button in the top-right corner of the navbar
2. Enter the credentials above
3. Click "Login" button in the modal
4. Premium sections will automatically unlock

**Visual Indicators:**
- Premium sections show a yellow "🔒 Premium" badge
- When logged in, the "Login" button changes to "Logout"
- Locked sections are hidden until you log in

## 🎯 User Flow

### First-Time User
1. **Land on Homepage** → See Top 20 stocks and basic features
2. **Explore Free Features** → View predictions and indicators
3. **Notice Premium Badges** → See locked sections with 🔒 Premium badges
4. **Click Login** → Modal opens with demo credentials displayed
5. **Enter Credentials** → Username: admin, Password: password
6. **Access Unlocked** → All premium features become visible

### Returning User
1. **Check Login Status** → App remembers your session
2. **If Logged Out** → Click Login button to re-authenticate
3. **If Logged In** → All features immediately available

## 🛠️ Technical Implementation

### Authentication Flow
```
User clicks Login
  ↓
Modal opens with credentials hint
  ↓
User submits form
  ↓
POST /login (username, password)
  ↓
Server validates credentials
  ↓
Session created (Flask session)
  ↓
Frontend receives success response
  ↓
updateAuthUI() called
  ↓
Enhanced sections revealed (.enhanced-only)
```

### Session Management
- **Technology:** Flask server-side sessions
- **Storage:** Secure HTTP-only cookies
- **Duration:** Until browser close or explicit logout
- **Security:** Session secret key (change in production!)

### Frontend Logic
```javascript
// On page load
checkAuthStatus() → GET /check_auth
  ↓
isLoggedIn = response.logged_in
  ↓
updateAuthUI()
  ↓
Show/hide .enhanced-only elements
```

## 📝 For Developers

### Adding New Premium Features
1. Add `enhanced-only` class to the HTML element
2. Add premium badge to header: `<span class="badge bg-warning text-dark ms-2"><i class="fas fa-lock"></i> Premium</span>`
3. Feature will automatically be hidden/shown based on login status

### Modifying Login Credentials
**File:** `app.py`
**Line:** ~616
```python
if username == 'admin' and password == 'password':
    session['logged_in'] = True
```

### Production Checklist
- [ ] Change `app.secret_key` to environment variable
- [ ] Implement proper user database
- [ ] Add password hashing (bcrypt/argon2)
- [ ] Implement rate limiting on login endpoint
- [ ] Add CSRF protection
- [ ] Set secure cookie flags (httpOnly, secure, sameSite)
- [ ] Add session timeout
- [ ] Implement "Remember Me" functionality
- [ ] Add password reset flow
- [ ] Add email verification

## 🎨 UI/UX Best Practices

### Visual Hierarchy
1. **Free sections** → Always visible, no badges
2. **Premium sections** → Yellow "🔒 Premium" badge in header
3. **Login button** → Prominent in navbar
4. **Credentials hint** → Displayed in login modal

### User Guidance
- Tooltips explain what each feature does
- Premium badges clearly indicate locked content
- Login modal shows demo credentials upfront
- Success/error notifications for login attempts

### Accessibility
- Proper ARIA labels on modal
- Keyboard navigation support
- Focus management in modal
- Screen reader friendly

## 🐛 Troubleshooting

### Login button not working
- Check browser console for JavaScript errors
- Verify `loginModal` exists in DOM
- Check Flask session secret key is set

### Premium sections not showing after login
- Verify `isLoggedIn` variable is true
- Check `.enhanced-only` class is applied correctly
- Inspect `updateAuthUI()` function execution

### Session not persisting
- Check Flask `app.secret_key` is set
- Verify cookies are enabled in browser
- Check for CORS issues if frontend/backend on different domains

## 📚 Related Documentation
- [README.md](../README.md) - Full project documentation
- [Product_Requirements_Document.md](Product_Requirements_Document.md) - Product specs
- [Technical_Documentation.md](Technical_Documentation.md) - Technical details
