document.addEventListener('DOMContentLoaded', function() {
  // Dropdown için event listener
  const dropdowns = document.querySelectorAll('.dropdown');

  dropdowns.forEach(dropdown => {
    // Fare ile üzerine gelindiğinde dropdown'ı göster
    dropdown.addEventListener('mouseenter', function() {
      const dropdownContent = this.querySelector('.dropdown-content');
      if (dropdownContent) {
        dropdownContent.style.display = 'block';
      }
    });

    // Fare ile üzerinden çekildiğinde dropdown'ı gizle
    dropdown.addEventListener('mouseleave', function() {
      const dropdownContent = this.querySelector('.dropdown-content');
      if (dropdownContent) {
        dropdownContent.style.display = 'none';
      }
    });
  });

  // Submenu için event listener
  const submenus = document.querySelectorAll('.dropdown-submenu');

  submenus.forEach(submenu => {
    // Fare ile üzerine gelindiğinde submenu'yü göster
    submenu.addEventListener('mouseenter', function() {
      const submenuContent = this.querySelector('.submenu-content');
      if (submenuContent) {
        submenuContent.style.display = 'block';
      }
    });

    // Fare ile üzerinden çekildiğinde submenu'yü gizle
    submenu.addEventListener('mouseleave', function() {
      const submenuContent = this.querySelector('.submenu-content');
      if (submenuContent) {
        submenuContent.style.display = 'none';
      }
    });
  });
});