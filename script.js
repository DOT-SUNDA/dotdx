// DOM Elements
const mobileMenu = document.getElementById('mobile-menu');
const navMenu = document.getElementById('nav-menu');
const searchInput = document.getElementById('search-input');
const productsGrid = document.getElementById('products-grid');
const searchResults = document.getElementById('search-results');
const noResults = document.getElementById('no-results');
const searchQuery = document.getElementById('search-query');

// Global products variable
let products = [];

// Load products from JSON file
async function loadProducts() {
    try {
        const response = await fetch('products.json');
        if (!response.ok) {
            throw new Error('Failed to load products');
        }
        products = await response.json();
        displayProducts(products);
        animateOnScroll();
    } catch (error) {
        console.error('Error loading products:', error);
        noResults.style.display = 'block';
        noResults.innerHTML = `
            <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
            <h3>Gagal memuat produk</h3>
            <p>Silakan coba refresh halaman</p>
        `;
    }
}

// Load produk saat halaman dimuat
document.addEventListener('DOMContentLoaded', loadProducts);

// Fungsi untuk menampilkan produk
function displayProducts(productsToDisplay) {
    productsGrid.innerHTML = '';
    
    if (productsToDisplay.length === 0) {
        noResults.style.display = 'block';
        productsGrid.style.display = 'none';
    } else {
        noResults.style.display = 'none';
        productsGrid.style.display = 'grid';
        
        productsToDisplay.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card fade-in';
            
            // Format harga
            const formattedPrice = new Intl.NumberFormat('id-ID', {
                style: 'currency',
                currency: 'IDR',
                maximumFractionDigits: 0
            }).format(product.price);
            
            const formattedOriginalPrice = new Intl.NumberFormat('id-ID', {
                style: 'currency',
                currency: 'IDR',
                maximumFractionDigits: 0
            }).format(product.originalPrice);
            
            // Buat rating bintang
            let stars = '';
            const fullStars = Math.floor(product.rating);
            const hasHalfStar = product.rating % 1 !== 0;
            
            for (let i = 0; i < fullStars; i++) {
                stars += '<i class="fas fa-star"></i>';
            }
            
            if (hasHalfStar) {
                stars += '<i class="fas fa-star-half-alt"></i>';
            }
            
            for (let i = 0; i < 5 - Math.ceil(product.rating); i++) {
                stars += '<i class="far fa-star"></i>';
            }
            
            // Tambahkan badge jika ada
            const badge = product.badge ? `<div class="product-badge">${product.badge}</div>` : '';
            
            productCard.innerHTML = `
                ${badge}
                <div class="product-image" style="background-image: url('${product.image}');"></div>
                <div class="product-info">
                    <span class="product-category">${product.category}</span>
                    <h3>${product.name}</h3>
                    <div class="product-price">
                        <span class="current-price">${formattedPrice}</span>
                        <span class="original-price">${formattedOriginalPrice}</span>
                    </div>
                    <div class="product-rating">
                        ${stars} <span>(${product.reviews})</span>
                    </div>
                    <a href="${product.link}" class="product-button">Beli Sekarang</a>
                </div>
            `;
            
            productsGrid.appendChild(productCard);
        });
    }
}

// Fungsi pencarian produk
function searchProducts(query) {
    const searchTerm = query.toLowerCase().trim();
    
    if (searchTerm === '') {
        searchResults.style.display = 'none';
        displayProducts(products);
        return;
    }
    
    const filteredProducts = products.filter(product => {
        return (
            product.name.toLowerCase().includes(searchTerm) ||
            product.category.toLowerCase().includes(searchTerm) ||
            (product.badge && product.badge.toLowerCase().includes(searchTerm))
        );
    });
    
    searchQuery.textContent = searchTerm;
    searchResults.style.display = 'block';
    displayProducts(filteredProducts);
}

// Event listener untuk search input
searchInput.addEventListener('input', function() {
    searchProducts(this.value);
});

// Mobile Menu Toggle
mobileMenu.addEventListener('click', function() {
    this.classList.toggle('active');
    navMenu.classList.toggle('active');
    
    // Animate hamburger icon
    const spans = this.querySelectorAll('span');
    if(this.classList.contains('active')) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
    } else {
        spans.forEach(span => {
            span.style.transform = '';
            span.style.opacity = '';
        });
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if(targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if(targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 70,
                behavior: 'smooth'
            });
            
            // Close mobile menu if open
            if(navMenu.classList.contains('active')) {
                mobileMenu.click();
            }
        }
    });
});

// Add shadow to header on scroll
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if(window.scrollY > 50) {
        header.style.boxShadow = '0 2px 15px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.05)';
    }
});

// Animation on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.fade-in');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.2;
        
        if(elementPosition < screenPosition) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
}

window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);