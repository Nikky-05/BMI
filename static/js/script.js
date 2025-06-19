// BMI Calculator Application
class BMICalculator {
    constructor() {
        this.form = document.getElementById('bmiForm');
        this.resultsSection = document.getElementById('results');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.init();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.addSmoothScrolling();
        this.addAnimationOnScroll();
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = this.getFormData();
        if (!this.validateForm(formData)) {
            return;
        }

        this.showLoading();
        
        try {
            const result = await this.calculateBMI(formData);
            this.displayResults(result);
            this.scrollToResults();
        } catch (error) {
            this.showError('Failed to calculate BMI. Please try again.');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
        }
    }

    getFormData() {
        return {
            gender: document.getElementById('gender').value,
            height: parseFloat(document.getElementById('height').value),
            weight: parseFloat(document.getElementById('weight').value)
        };
    }

    validateForm(data) {
        if (!data.gender) {
            this.showError('Please select your gender.');
            return false;
        }
        
        if (!data.height || data.height < 100 || data.height > 250) {
            this.showError('Please enter a valid height between 100-250 cm.');
            return false;
        }
        
        if (!data.weight || data.weight < 30 || data.weight > 300) {
            this.showError('Please enter a valid weight between 30-300 kg.');
            return false;
        }
        
        return true;
    }

    async calculateBMI(data) {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return await response.json();
    }

    displayResults(result) {
        if (!result.success) {
            this.showError(result.error || 'An error occurred');
            return;
        }

        // Update BMI display
        document.getElementById('bmiValue').textContent = result.bmi;
        document.getElementById('bmiCategory').textContent = result.diet_details.category;
        
        // Update BMI category color
        const categoryElement = document.getElementById('bmiCategory');
        categoryElement.className = `bmi-category ${this.getBMICategoryClass(result.bmi)}`;

        // Display diet recommendations
        this.displayDietRecommendations(result.diet_details);
        
        // Show results section with animation
        this.resultsSection.style.display = 'block';
        setTimeout(() => {
            this.resultsSection.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }

    getBMICategoryClass(bmi) {
        if (bmi < 18.5) return 'underweight';
        if (bmi < 25) return 'normal';
        if (bmi < 30) return 'overweight';
        return 'obese';
    }

    displayDietRecommendations(details) {
        const container = document.getElementById('dietDetails');
        
        container.innerHTML = `
            <div class="diet-overview mb-4">
                <div class="row">
                    <div class="col-md-6">
                        <div class="info-card">
                            <h6><i class="fas fa-info-circle me-2"></i>Category</h6>
                            <p class="mb-0">${details.category}</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="info-card">
                            <h6><i class="fas fa-chart-bar me-2"></i>BMI Range</h6>
                            <p class="mb-0">${details.bmi_range}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="recommendations-grid">
                <div class="recommendation-section">
                    <h6><i class="fas fa-lightbulb me-2 text-warning"></i>General Recommendations</h6>
                    <ul class="recommendation-list">
                        ${details.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>

                <div class="recommendation-section">
                    <h6><i class="fas fa-check-circle me-2 text-success"></i>Foods to Include</h6>
                    <div class="food-tags">
                        ${details.foods_to_include.map(food => `<span class="food-tag include">${food}</span>`).join('')}
                    </div>
                </div>

                <div class="recommendation-section">
                    <h6><i class="fas fa-times-circle me-2 text-danger"></i>Foods to Avoid</h6>
                    <div class="food-tags">
                        ${details.foods_to_avoid.map(food => `<span class="food-tag avoid">${food}</span>`).join('')}
                    </div>
                </div>
            </div>

            <div class="disclaimer mt-4">
                <div class="alert alert-info">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Disclaimer:</strong> These recommendations are for informational purposes only. 
                    Please consult with a healthcare professional before making significant dietary changes.
                </div>
            </div>
        `;

        // Add custom styles for the new elements
        this.addDynamicStyles();
    }

    addDynamicStyles() {
        if (!document.getElementById('dynamicStyles')) {
            const style = document.createElement('style');
            style.id = 'dynamicStyles';
            style.textContent = `
                .info-card {
                    background: var(--light-gray);
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid var(--accent-color);
                }

                .info-card h6 {
                    color: var(--text-dark);
                    margin-bottom: 8px;
                    font-weight: 600;
                }

                .recommendations-grid {
                    display: grid;
                    gap: 25px;
                }

                .recommendation-section {
                    background: var(--white);
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: var(--shadow-light);
                    border: 1px solid rgba(0,0,0,0.05);
                }

                .recommendation-list {
                    list-style: none;
                    padding: 0;
                    margin: 15px 0 0 0;
                }

                .recommendation-list li {
                    padding: 8px 0;
                    border-bottom: 1px solid #f0f0f0;
                    position: relative;
                    padding-left: 20px;
                }

                .recommendation-list li:before {
                    content: '✓';
                    position: absolute;
                    left: 0;
                    color: var(--accent-color);
                    font-weight: bold;
                }

                .recommendation-list li:last-child {
                    border-bottom: none;
                }

                .food-tags {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-top: 15px;
                }

                .food-tag {
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    font-weight: 500;
                    transition: all 0.3s ease;
                }

                .food-tag.include {
                    background: rgba(40, 167, 69, 0.1);
                    color: #28a745;
                    border: 1px solid rgba(40, 167, 69, 0.3);
                }

                .food-tag.avoid {
                    background: rgba(220, 53, 69, 0.1);
                    color: #dc3545;
                    border: 1px solid rgba(220, 53, 69, 0.3);
                }

                .food-tag:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }

                .bmi-category.underweight { color: #17a2b8; }
                .bmi-category.normal { color: #28a745; }
                .bmi-category.overweight { color: #ffc107; }
                .bmi-category.obese { color: #dc3545; }

                .disclaimer {
                    margin-top: 30px;
                }

                @media (max-width: 768px) {
                    .food-tags {
                        justify-content: center;
                    }
                    
                    .recommendation-section {
                        padding: 15px;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    scrollToResults() {
        setTimeout(() => {
            this.resultsSection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }, 300);
    }

    showLoading() {
        this.loadingSpinner.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    hideLoading() {
        this.loadingSpinner.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    showError(message) {
        // Create and show error toast
        const toast = document.createElement('div');
        toast.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        toast.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    addSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    addAnimationOnScroll() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.feature-item, .stat-card, .calculator-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s ease';
            observer.observe(el);
        });
    }
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(107, 142, 35, 0.95)';
        navbar.style.backdropFilter = 'blur(10px)';
    } else {
        navbar.style.background = 'var(--gradient-primary)';
        navbar.style.backdropFilter = 'none';
    }
});

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BMICalculator();
    
    // Add some interactive effects
    addInteractiveEffects();
});

function addInteractiveEffects() {
    // Parallax effect for hero section
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.hero-section');
        if (parallax) {
            const speed = scrolled * 0.5;
            parallax.style.transform = `translateY(${speed}px)`;
        }
    });

    // Add hover effects to cards
    document.querySelectorAll('.calculator-card, .results-card, .feature-item').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255,255,255,0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Add ripple animation keyframes
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

