document.addEventListener("DOMContentLoaded", function () {
  const filterContainer = document.querySelector(".fee-due-range-filter");
  if (filterContainer) {
    const rangeForm = document.createElement("form");
    rangeForm.className = "fee-range-filter";
    rangeForm.innerHTML = `
            <label>Custom Fee Range:</label><br>
            <input type="number" name="min_fee" placeholder="Min Fee" min="0">
            <span>to</span>
            <input type="number" name="max_fee" placeholder="Max Fee" min="0">
            <button type="submit">Filter</button>
        `;
    filterContainer.appendChild(rangeForm);

    rangeForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const minFee = this.elements.min_fee.value;
      const maxFee = this.elements.max_fee.value;
      if (minFee || maxFee) {
        let url = new URL(window.location.href);
        if (minFee) url.searchParams.set("min_fee", minFee);
        if (maxFee) url.searchParams.set("max_fee", maxFee);
        window.location.href = url.toString();
      }
    });
  }
});
