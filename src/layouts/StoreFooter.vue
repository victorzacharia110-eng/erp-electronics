<template>
  <footer class="site-footer">
    <div class="footer-main">
      <div class="container footer-grid">
        <div class="footer-brand">
          <div class="footer-logo">
            <span class="logo-icon"><i class="fas fa-bolt"></i></span>
            <span class="logo-text">Electro<span>Shop</span></span>
          </div>
          <p>Your trusted source for quality electronics and phone accessories in Tanzania. We offer the best prices and fast delivery.</p>
          <div class="footer-social">
            <a href="#"><i class="fab fa-facebook-f"></i></a>
            <a href="#"><i class="fab fa-whatsapp"></i></a>
            <a href="#"><i class="fab fa-instagram"></i></a>
            <a href="#"><i class="fab fa-twitter"></i></a>
          </div>
        </div>

        <div class="footer-links">
          <h4>Quick Links</h4>
          <router-link to="/">Home</router-link>
          <router-link to="/products">Products</router-link>
          <router-link to="/cart">Cart</router-link>
          <router-link to="/orders">My Orders</router-link>
        </div>

        <div class="footer-links">
          <h4>Categories</h4>
          <router-link to="/category/phones">Phones</router-link>
          <router-link to="/category/accessories">Accessories</router-link>
          <router-link to="/category/audio">Audio</router-link>
          <router-link to="/category/wearables">Wearables</router-link>
        </div>

        <div class="footer-contact">
          <h4>Contact Us</h4>
          <p><i class="fas fa-location-dot"></i> Dar es Salaam, Tanzania</p>
          <p><i class="fas fa-phone"></i> +255 703 870 268</p>
          <p><i class="fas fa-envelope"></i> info@electroshop.co.tz</p>
          <div class="payment-methods">
            <span class="payment-label">We Accept:</span>
            <div class="payment-icons">
              <i class="fas fa-mobile-screen"></i> M-Pesa
              <i class="fas fa-mobile"></i> Tigo
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="container footer-bottom-inner">
        <p>&copy; {{ new Date().getFullYear() }} ElectroShop. All rights reserved.</p>
        <div class="footer-bottom-links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms & Conditions</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  background: #2c3e50;
  color: #fff;
  margin-top: auto;
}

.footer-main {
  padding: 48px 0 32px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 40px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.footer-logo .logo-icon {
  color: #fff;
  background: #e74c3c;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  font-size: 16px;
}

.footer-logo .logo-text {
  font-size: 20px;
  font-weight: 800;
  color: #fff;
}

.footer-logo .logo-text span {
  color: #e74c3c;
}

.footer-brand p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  line-height: 1.7;
  margin-bottom: 16px;
}

.footer-social {
  display: flex;
  gap: 10px;
}

.footer-social a {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  transition: all 0.2s;
}

.footer-social a:hover {
  background: #e74c3c;
}

.footer-links h4,
.footer-contact h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
}

.footer-links a {
  display: block;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  padding: 5px 0;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: #e74c3c;
}

.footer-contact p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  padding: 5px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-contact p i {
  color: #e74c3c;
  width: 16px;
}

.payment-methods {
  margin-top: 16px;
}

.payment-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  display: block;
  margin-bottom: 8px;
}

.payment-icons {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 0;
}

.footer-bottom-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-bottom p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.footer-bottom-links {
  display: flex;
  gap: 20px;
}

.footer-bottom-links a {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  transition: color 0.2s;
}

.footer-bottom-links a:hover {
  color: #e74c3c;
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  .footer-brand {
    grid-column: 1 / -1;
  }

  .footer-bottom-inner {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}
</style>
