/**
* Template Name: Delicious
* Template URL: https://bootstrapmade.com/delicious-free-restaurant-bootstrap-theme/
* Updated: May 16 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/




(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    let selectEl = select(el, all)
    if (selectEl) {
      if (all) {
        selectEl.forEach(e => e.addEventListener(type, listener))
      } else {
        selectEl.addEventListener(type, listener)
      }
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select('#navbar .scrollto', true)
  const navbarlinksActive = () => {
    let position = window.scrollY + 200
    navbarlinks.forEach(navbarlink => {
      if (!navbarlink.hash) return
      let section = select(navbarlink.hash)
      if (!section) return
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        navbarlink.classList.add('active')
      } else {
        navbarlink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navbarlinksActive)
  onscroll(document, navbarlinksActive)

  /**
   * Scrolls to an element with header offset
   */
  const scrollto = (el) => {
    let header = select('#header')
    let offset = header.offsetHeight

    let elementPos = select(el).offsetTop
    window.scrollTo({
      top: elementPos - offset,
      behavior: 'smooth'
    })
  }

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  let selectTopbar = select('#topbar')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
        if (selectTopbar) {
          selectTopbar.classList.add('topbar-scrolled')
        }
      } else {
        selectHeader.classList.remove('header-scrolled')
        if (selectTopbar) {
          selectTopbar.classList.remove('topbar-scrolled')
        }
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Mobile nav toggle
   */
  on('click', '.mobile-nav-toggle', function(e) {
    select('#navbar').classList.toggle('navbar-mobile')
    this.classList.toggle('bi-list')
    this.classList.toggle('bi-x')
  })

  /**
   * Mobile nav dropdowns activate
   */
  on('click', '.navbar .dropdown > a', function(e) {
    if (select('#navbar').classList.contains('navbar-mobile')) {
      e.preventDefault()
      this.nextElementSibling.classList.toggle('dropdown-active')
    }
  }, true)

  /**
   * Scrool with ofset on links with a class name .scrollto
   */
  on('click', '.scrollto', function(e) {
    if (select(this.hash)) {
      e.preventDefault()

      let navbar = select('#navbar')
      if (navbar.classList.contains('navbar-mobile')) {
        navbar.classList.remove('navbar-mobile')
        let navbarToggle = select('.mobile-nav-toggle')
        navbarToggle.classList.toggle('bi-list')
        navbarToggle.classList.toggle('bi-x')
      }
      scrollto(this.hash)
    }
  }, true)

  /**
   * Scroll with ofset on page load with hash links in the url
   */
  window.addEventListener('load', () => {
    if (window.location.hash) {
      if (select(window.location.hash)) {
        scrollto(window.location.hash)
      }
    }
  });

  /**
   * Hero carousel indicators
   */
  let heroCarouselIndicators = select("#hero-carousel-indicators")
  let heroCarouselItems = select('#heroCarousel .carousel-item', true)

  heroCarouselItems.forEach((item, index) => {
    (index === 0) ?
    heroCarouselIndicators.innerHTML += "<li data-bs-target='#heroCarousel' data-bs-slide-to='" + index + "' class='active'></li>":
      heroCarouselIndicators.innerHTML += "<li data-bs-target='#heroCarousel' data-bs-slide-to='" + index + "'></li>"
  });

  /**
   * Menu isotope and filter
   */
  window.addEventListener('load', () => {
    let menuContainer = select('.menu-container');
    if (menuContainer) {
      let menuIsotope = new Isotope(menuContainer, {
        itemSelector: '.menu-item',
        layoutMode: 'fitRows'
      });

      let menuFilters = select('#menu-flters li', true);

      on('click', '#menu-flters li', function(e) {
        e.preventDefault();
        menuFilters.forEach(function(el) {
          el.classList.remove('filter-all');
        });
        this.classList.add('filter-all');

        menuIsotope.arrange({
          filter: this.getAttribute('data-filter')
        });

      }, true);
    }

  });

  /**
   * this is to activate the sub menu ---still in progress 
   */

  /**
   * Testimonials slider
   */
  new Swiper('.events-slider', {
    speed: 600,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    slidesPerView: 'auto',
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    }
  });

  /**
   * Initiate gallery lightbox 
   */
  const galleryLightbox = GLightbox({
    selector: '.gallery-lightbox'
  });

  /**
   * Initiate GLightbox 
   */
  GLightbox({
    selector: '.glightbox'
  });

  /**
   * Testimonials slider
   */
  new Swiper('.testimonials-slider', {
    speed: 600,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    slidesPerView: 'auto',
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    }
  });

})()


/*

-----------------------------------------order meal page-------------------------------------
*/






const extrasContainer = document.getElementById('extras-container');


const quantityInput = document.getElementById('quantity');
const totalPriceElement = document.getElementById('totalPrice');
let basePrice = 0; // Assuming base price of the meal is 10000 RWF
let originalPrice=0;
//const extraData = JSON.parse(document.getElementById('extra-data').textContent);
// Fetch the extras and display them for the current item
async function fetchExtras(menuItemId, price) {
  basePrice = price;
  originalPrice = price;

  try {
      const response = await fetch(`/get-extras/${menuItemId}/`);
      const data = await response.json();
      const extraData = data.extras;
     
      
      displayExtras(extraData);
  } catch (error) {
      console.error('Error fetching extras:', error);
  }
}






document.addEventListener('DOMContentLoaded', function() {
  // Get the edit order button
  const editOrderButton = document.getElementById('edit-order-btn');
  // Get the table header cell for "Action" column (7th column)
  const actionColumnHeader = document.querySelector('th:nth-child(1)');
  // Get all table rows (tr) in the body
  const tableRows = document.querySelectorAll('table tbody tr');
  // Get the Action column cells (7th column in each row)
  const actionColumnCells = Array.from(tableRows).map(row => row.querySelector('td:nth-child(1)'));

  // Toggle visibility of delete buttons when "Edit Order" is clicked
if (editOrderButton){
  editOrderButton.addEventListener('click', function() {
    const isHidden = actionColumnHeader.style.display === 'none' || actionColumnHeader.style.display === '';  // Check if the column is hidden

    // Show or hide the Action column header and all cells in that column
    actionColumnHeader.style.display = isHidden ? 'table-cell' : 'none';  // Toggle the header
    actionColumnCells.forEach(function(cell) {
        cell.style.display = isHidden ? 'table-cell' : 'none';  // Toggle all cells in this column
    });
});
}
});





//////////////////////////////////////////////////////////// add to order functions  ////////////////////////////////


function displayExtras(extraData) {
  const extrasContainer = document.getElementById('extras-container');
  extrasContainer.innerHTML = ''; // Clear the container

  if (extraData.length === 0) {
      extrasContainer.innerHTML = '<p>No extras available for this item.</p>';
  } else {
      extraData.forEach(extra => {
          const extraItem = document.createElement('div');
          extraItem.className = 'extra-item';
          extraItem.setAttribute('data-price', extra.price);
          extraItem.setAttribute('data-extra-id', extra.id);

          // Remove the quantity input and keep just the extra name and price
          extraItem.innerHTML = `
              ${extra.name} 
              <span class="price">+ ${extra.price.toLocaleString()} RWF
                  <span class="check-icon" style="display: none;">✔️</span>
              </span>
          `;

          // Add event listener to toggle selection on click
          extraItem.addEventListener('click', function() {
              this.classList.toggle('selected');
              const checkIcon = this.querySelector('.check-icon');
              checkIcon.style.display = this.classList.contains('selected') ? 'inline' : 'none';
              calculateTotal(); // Recalculate total when extra is added/removed
          });

          extrasContainer.appendChild(extraItem); // Append to the container
      });
  }
}



// Calculate total price, accounting for item quantity and selected extras with quantities
function calculateTotal() {
  let totalExtras = 0;
  const itemQuantity =   parseInt(document.getElementById('quantity').value) || 1
  document.querySelectorAll('.extra-item').forEach(item => {
  
      const extraPrice = parseInt(item.getAttribute('data-price'));
      const extraQuantity = itemQuantity;
      if (item.classList.contains('selected') ) {
      totalExtras += extraPrice ;
      } 
  });

  const quantity = parseInt(document.getElementById('quantity').value);
  const totalPrice = (basePrice + totalExtras) * quantity;
  document.getElementById('totalPrice').textContent = `Total: ${totalPrice.toLocaleString()} RWF`;
}
const addButton = document.getElementById('addButton');
// Add item to order with extras, quantity, and notes
if (addButton){
  addButton.addEventListener('click', async function() {

    const itemId = this.getAttribute('data-item-id');
    const url = this.getAttribute('data-url');
    const quantity = parseInt(document.getElementById('quantity').value);
    const notes = document.getElementById('notes').value;
  
    // Collect selected extras
    const extras = Array.from(document.querySelectorAll('.extra-item.selected')).map(item => ({
        id: item.getAttribute('data-extra-id'),
        
        quantity: quantity
    }));
    document.querySelectorAll('.extra-item.selected').forEach(item => {
    console.log("Element:", item); // Logs the element
    console.log("data-extra-id:", item.getAttribute('data-extra-id')); // Logs the attribute value
  });
  
    const data = {
        item_id: itemId,
        quantity: quantity,
        extras: extras,
        notes: notes

    };
  
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()  // Use the getCSRFToken function
            },
            body: JSON.stringify(data)
        });
  
        if (response.ok) {
          // Replace alert with custom success dialog
          showSuccessDialog({
              title: 'Success!',
              message: 'the Item was added to your order successfully!',
              okButtonText: 'OK',
              onOk: function() {
                  window.location.href = '/order_details/';
              },
              // autoHideDelay: 10000 // Optional: auto-hide after 2 seconds
          });
      }else {
            alert("Error adding item to order.");
        }
    } catch (error) {
        console.error("Error:", error);
    }
  });
}



if (addButton){
  document.getElementById('increment').addEventListener('click', function() {
    const quantityInput = document.getElementById('quantity');
    quantityInput.value = parseInt(quantityInput.value) + 1;
    calculateTotal();
  });
  
  document.getElementById('decrement').addEventListener('click', function() {
    const quantityInput = document.getElementById('quantity');
    if (parseInt(quantityInput.value) > 1) {
        quantityInput.value = parseInt(quantityInput.value) - 1;
        calculateTotal();
    }
  });
}

///////////////////////////////////////printing from the fromt end 
async function printOrder() {
  try {
    const response = await fetch('/print_order/'); // Fetch order details from your endpoint
    const data = await response.json();

    if (response.ok) {
      const { order_items, total_amount } = data;

      // Open a new window for printing
      const printWindow = window.open('', '_blank');
      if (!printWindow) {
        console.error('Unable to open print window.');
        return;
      }

      // Write content for the new window
      printWindow.document.write(`
        <html>
        <head>
          <title>Print Order</title>
          <style>
            @media print {
              @page {
                size: 88mm auto; /* Set custom page size */
                 margin: 5mm; 
              }
              body {
                margin: 2px;
                padding: 1px;
                width: 88mm; /* Ensure body matches the page size */
                max-width: 88mm;
                font-family: Arial, sans-serif;
　　 　 　 　 overflow: hidden; /* Prevent content overflow */
              }
              ul {
                list-style: none;
                padding: 1px;
                margin: 1px;
              }
              li {
                margin: 5px 0;
              }
              h1, p {
                margin-left:5px ;
                margin-right:5px ;
                padding: 5px;
              }
            }
          </style>
        </head>
        <body>
          <h1>Mocha Cafe</h1>
          <p>Date: ${new Date().toLocaleString()}</p>
          <hr>
          <ul>
            ${order_items
              .map(
                (item) =>
                  `<li>${item.quantity} x ${item.name} - ${item.subtotal} RWF</li>`
              )
              .join('')}
          </ul>
    <hr>
    <p><strong>Total:</strong> ${total_amount} RWF</p>
    <hr>
    <div class="bottom-line">
      Thank you for visiting Mocha Mocha Cafe!
    </div>
        </body>
        </html>
      `);

      printWindow.document.close();
      printWindow.print(); // Trigger the print dialog
    } else {
      console.error('Failed to fetch order details:', data.message);
    }
  } catch (error) {
    console.error('Error fetching order details:', error);
  }
}

///////////////////////////////////// profile page ///////////////////////////////////////////
// document.addEventListener("DOMContentLoaded", function() {
//   const editButton = document.getElementById("edit-btn");
//   const form = document.getElementById("profile-form");

//   // Check if the editButton exists
//   if (editButton && form) {

//     const formElements = form.querySelectorAll("input, button[type='submit']");

//     // Disable the form elements initially
//     formElements.forEach(element => {
//       element.disabled = true;
//     });

//     // Enable the form when the "Edit" button is clicked
//     editButton.addEventListener("click", function() {
    
//       formElements.forEach(element => {
//         element.disabled = false;
//       });

//       // Hide the edit button after it's clicked
//       editButton.style.display = "none"; 
//     });
//   } else {
//     console.log("Edit button or form not found.");
//   }
// });

document.addEventListener('DOMContentLoaded', function() {
  
    // Initialize mobile nav
    initializeMobileNav();
});

/**
 * Mobile Navigation
 */
function initializeMobileNav() {
  const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
  const navbar = document.querySelector('#navbar'); // Select the navbar
  const navLinks = document.querySelectorAll('#navbar .scrollto'); // Select all nav links

  if (mobileNavToggle) {
    mobileNavToggle.addEventListener('click', function(e) {
        document.body.classList.toggle('mobile-nav-active');
        
       
        if (this.className.includes('bi-list')) {
            this.className = this.className.replace('bi-list', 'bi-x');
        } else {
            this.className = this.className.replace('bi-x', 'bi-list');
        }
    });
}

  // Close the mobile menu and revert icon when a link is clicked
  navLinks.forEach(link => {
      link.addEventListener('click', () => {
          document.body.classList.remove('mobile-nav-active'); // Hide the mobile menu
          mobileNavToggle.classList.remove('bi-x'); // Revert to hamburger icon
          mobileNavToggle.classList.add('bi-list'); // Ensure hamburger icon is visible
      });
  });
}

// Handle Status Updates in Dashboard
document.addEventListener('DOMContentLoaded', function() {
    const statusOptions = document.querySelectorAll('.status-option');
    if (statusOptions) {
        statusOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const orderId = this.dataset.orderId;
                const status = this.dataset.status;
                updateOrderStatus(orderId, status);
            });
        });
    }
});

/**
 * Update Order Status
 */
function updateOrderStatus(orderId, status) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/update_order_status/${orderId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI
            const statusBadge = document.querySelector(`[data-order-id="${orderId}"]`).closest('tr').querySelector('.badge');
            statusBadge.textContent = status;
            // Update badge class
            statusBadge.className = `badge ${getStatusClass(status)}`;
        }
    })
    .catch(error => console.error('Error:', error));
}

/**
 * Get Status Badge Class
 */
function getStatusClass(status) {
    switch(status.toLowerCase()) {
        case 'pending':
            return 'badge-pending';
        case 'in progress':
            return 'badge-progress';
        case 'served':
            return 'badge-served';
        default:
            return 'bg-secondary';
    }
}



/////////////////////////////////// menu search bar ///////////////////////
document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('menu-search');
  if (searchInput) {
    let menuIsotope = null;
    const menuContainer = document.querySelector('.menu-container');
    if (window.Isotope && menuContainer) {
      // Always create or get the Isotope instance
      menuIsotope = Isotope.data(menuContainer) || new Isotope(menuContainer, {
        itemSelector: '.menu-item',
        layoutMode: 'fitRows'
      });
    }

    searchInput.addEventListener('input', function () {
      const query = this.value.toLowerCase();
      if (menuIsotope) {
        menuIsotope.arrange({
          filter: function(itemElem) {
            const nameElem = itemElem.querySelector('.item-name');
            const name = nameElem ? nameElem.textContent.toLowerCase() : '';
            return name.includes(query);
          }
        });
      } else {
        // fallback if Isotope is not available
        document.querySelectorAll('.menu-item').forEach(function (item) {
          const name = item.querySelector('.item-name')?.textContent.toLowerCase() || '';
          if (name.includes(query)) {
            item.style.display = '';
          } else {
            item.style.display = 'none';
          }
        });
      }
    });
  }
});
