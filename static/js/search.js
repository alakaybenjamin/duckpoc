// Global state
let searchTerms = [];
let currentPage = 1;
let currentCategory = 'all';
let isLoading = false;
let debounceTimer;

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const searchResults = document.getElementById('searchResults');
    const searchPills = document.getElementById('searchPills');
    const paginationContainer = document.getElementById('pagination');
    const suggestionsContainer = document.getElementById('suggestions');

    // Add a new search term
    function addSearchTerm(term) {
        const trimmedTerm = term.trim();
        if (!trimmedTerm || searchTerms.includes(trimmedTerm)) return;

        if (searchTerms.length >= 3) {
            alert('Maximum 3 search terms allowed');
            return;
        }

        searchTerms.push(trimmedTerm);
        searchInput.value = '';
        updateSearchPills();
        performSearch();
    }

    // Update the search pills display
    function updateSearchPills() {
        if (!searchPills) return;
        searchPills.innerHTML = searchTerms.map(term => `
            <div class="search-pill">
                ${term}
                <button type="button" class="btn-close btn-close-white" 
                        aria-label="Remove" onclick="removeSearchTerm('${term}')"></button>
            </div>
        `).join('');
    }

    // Remove a search term
    window.removeSearchTerm = function(term) {
        searchTerms = searchTerms.filter(t => t !== term);
        updateSearchPills();
        if (searchTerms.length > 0) {
            performSearch();
        } else {
            clearSearch();
        }
    };

    // Clear all search
    function clearSearch() {
        searchTerms = [];
        searchPills.innerHTML = '';
        searchResults.innerHTML = '';
        searchInput.value = '';
        if (paginationContainer) paginationContainer.innerHTML = '';
    }

    // Perform search
    async function performSearch() {
        if (searchTerms.length === 0 || isLoading) return;

        try {
            isLoading = true;
            showLoading();

            // Get filter values
            const status = document.getElementById('statusFilter')?.value;
            const phase = document.getElementById('phaseFilter')?.value;
            const startDate = document.getElementById('startDateFilter')?.value;
            const endDate = document.getElementById('endDateFilter')?.value;
            const indicationCategory = document.getElementById('indicationCategoryFilter')?.value;
            const severity = document.getElementById('severityFilter')?.value;
            const procedureCategory = document.getElementById('procedureCategoryFilter')?.value;
            const riskLevel = document.getElementById('riskLevelFilter')?.value;
            const minDuration = document.getElementById('minDurationFilter')?.value;
            const maxDuration = document.getElementById('maxDurationFilter')?.value;

            // Build URL parameters
            const params = new URLSearchParams({
                q: searchTerms.join(' OR '),
                page: currentPage.toString(),
                per_page: '10',
                category: currentCategory
            });

            // Add filters if they have values
            if (status) params.append('status', status);
            if (phase) params.append('phase', phase);
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            if (indicationCategory) params.append('indication_category', indicationCategory);
            if (severity) params.append('severity', severity);
            if (procedureCategory) params.append('procedure_category', procedureCategory);
            if (riskLevel) params.append('risk_level', riskLevel);
            if (minDuration) params.append('min_duration', minDuration);
            if (maxDuration) params.append('max_duration', maxDuration);

            const response = await fetch(`/api/search?${params.toString()}`);

            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            displayResults(data);
            displayPagination(data);
        } catch (error) {
            console.error('Search error:', error);
            searchResults.innerHTML = '<p class="text-danger">Search failed. Please try again.</p>';
        } finally {
            isLoading = false;
            hideLoading();
        }
    }

    // Event listeners
    searchButton?.addEventListener('click', () => {
        const term = searchInput?.value;
        if (term) addSearchTerm(term);
    });

    searchInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const term = searchInput?.value;
            if (term) addSearchTerm(term);
        }
    });

    // Initialize filters
    const filterIds = [
        'statusFilter', 'phaseFilter', 'startDateFilter', 'endDateFilter',
        'indicationCategoryFilter', 'severityFilter', 'procedureCategoryFilter',
        'riskLevelFilter', 'minDurationFilter', 'maxDurationFilter'
    ];

    filterIds.forEach(filterId => {
        const element = document.getElementById(filterId);
        if (element) {
            element.addEventListener('change', () => {
                if (searchTerms.length > 0) {
                    performSearch();
                }
            });
        }
    });

    // Loading spinner
    const loadingSpinner = document.createElement('div');
    loadingSpinner.className = 'spinner-border text-primary';
    loadingSpinner.setAttribute('role', 'status');
    loadingSpinner.innerHTML = '<span class="visually-hidden">Loading...</span>';

    function showLoading() {
        if (!searchResults) return;
        searchResults.innerHTML = '';
        searchResults.appendChild(loadingSpinner);
    }

    function hideLoading() {
        if (searchResults?.contains(loadingSpinner)) {
            searchResults.removeChild(loadingSpinner);
        }
    }

    // Display results
    function displayResults(data) {
        console.log('Displaying results:', data); // Add logging
        if (!searchResults) {
            console.error('Search results container not found!');
            return;
        }

        if (!data.results || data.results.length === 0) {
            searchResults.innerHTML = '<p class="text-center">No results found</p>';
            return;
        }

        const resultsHtml = data.results.map(result => `
            <div class="search-result-item mb-4 p-3 border rounded bg-light">
                <h4 class="mb-2">${result.title}</h4>
                <div class="result-metadata mb-2">
                    <span class="badge bg-primary me-2">${result.type}</span>
                    ${result.phase ? `<span class="badge bg-secondary me-2">Phase: ${result.phase}</span>` : ''}
                    ${result.status ? `<span class="badge bg-info me-2">Status: ${result.status}</span>` : ''}
                </div>
                ${result.description ? `<p class="result-description mb-2">${result.description}</p>` : ''}
                ${result.data_products ? `
                    <div class="data-products mt-2">
                        <h5 class="mb-2">Available Data Products:</h5>
                        ${result.data_products.map(product => `
                            <div class="data-product-item" data-product-id="${product.id}">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="dp-${product.id}">
                                    <label class="form-check-label" for="dp-${product.id}">
                                        ${product.title} (${product.type})
                                    </label>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');

        searchResults.innerHTML = resultsHtml;
        console.log('Results rendered to DOM'); // Add logging

        // Add checkbox event listeners and update menu visibility
        const checkboxes = document.querySelectorAll('.form-check-input');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                updateMenuVisibility();
                updateSelectedItemsList();
            });
        });
    }

    function updateSelectedItemsList() {
        const selectedItemsList = document.getElementById('selectedItemsList');
        if (!selectedItemsList) return;

        const checkedProducts = document.querySelectorAll('.form-check-input:checked');
        const items = Array.from(checkedProducts).map(checkbox => {
            const label = checkbox.closest('.data-product-item').querySelector('.form-check-label').textContent.trim();
            return `<div class="selected-item">${label}</div>`;
        });

        selectedItemsList.innerHTML = items.length > 0
            ? items.join('')
            : '<p class="text-muted">No items selected</p>';
    }


    function updateMenuVisibility() {
        const actionsMenu = document.querySelector('.actions-menu');
        if (actionsMenu) {
            const hasCheckedItems = document.querySelectorAll('.form-check-input:checked').length > 0;
            actionsMenu.classList.toggle('d-none', !hasCheckedItems);
        }
    }

    // Display pagination
    function displayPagination(data) {
        if (!data.total || !paginationContainer) return;

        const totalPages = Math.ceil(data.total / 10);
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        const paginationHtml = `
            <nav>
                <ul class="pagination justify-content-center">
                    <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                        <a class="page-link" href="#" onclick="searchPage(${currentPage - 1})">Previous</a>
                    </li>
                    ${Array.from({length: totalPages}, (_, i) => i + 1).map(page => `
                        <li class="page-item ${page === currentPage ? 'active' : ''}">
                            <a class="page-link" href="#" onclick="searchPage(${page})">${page}</a>
                        </li>
                    `).join('')}
                    <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                        <a class="page-link" href="#" onclick="searchPage(${currentPage + 1})">Next</a>
                    </li>
                </ul>
            </nav>
        `;

        paginationContainer.innerHTML = paginationHtml;
    }

    // Pagination handler
    window.searchPage = function(page) {
        if (page < 1) return;
        currentPage = page;
        performSearch();
    };

    //Suggestion Handling (from original code)
    function debounceSearch() {
        clearTimeout(debounceTimer);
        const query = searchInput?.value.trim();

        if (query.length < 2) {
            if (suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
            }
            return;
        }

        debounceTimer = setTimeout(() => fetchSuggestions(query), 300);
    }

    async function fetchSuggestions(query) {
        if (!suggestionsContainer) return;

        try {
            const response = await fetch(`/api/suggest?q=${encodeURIComponent(query)}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            if (data.suggestions && data.suggestions.length > 0) {
                displaySuggestions(data.suggestions);
            } else {
                suggestionsContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error.message);
            suggestionsContainer.style.display = 'none';
        }
    }

    function displaySuggestions(suggestions) {
        if (!suggestionsContainer || !searchInput) return;

        suggestionsContainer.innerHTML = '';
        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.innerHTML = `
                <span class="suggestion-text">${suggestion.text}</span>
                <span class="suggestion-type">${suggestion.type}</span>
            `;

            div.addEventListener('click', () => {
                if (searchInput) {
                    searchInput.value = suggestion.text;
                    suggestionsContainer.style.display = 'none';
                    performSearch();
                }
            });

            suggestionsContainer.appendChild(div);
        });

        suggestionsContainer.style.display = 'block';
    }

    //Rest of the code from original (unchanged)
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        document.querySelector('.search-container').insertBefore(errorDiv, searchResults);
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        document.querySelector('.search-container').insertBefore(successDiv, searchResults);
        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }

    window.addToCollection = addToCollection;


    // Initialize category selection
    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            currentCategory = button.getAttribute('data-category');
            if (searchInput.value.trim()) {
                performSearch();
            }
        });
    });

    // Create search actions menu
    const searchContainer = document.querySelector('.search-container');
    if (searchContainer) {
        // Add menu before search results
        const actionsMenu = document.createElement('div');
        actionsMenu.className = 'search-actions-menu mt-3 mb-3 d-none actions-menu'; // Corrected class name
        actionsMenu.innerHTML = `
            <div class="d-flex justify-content-end">
                <div class="dropdown">
                    <button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                        Actions
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="#" id="addToCollectionMenuItem">
                            <i class="bi bi-plus-circle me-2"></i>Add to Collection
                        </a></li>
                    </ul>
                </div>
            </div>
        `;

        // Insert menu after search box but before results
        const searchBox = searchContainer.querySelector('.search-box-container') || searchContainer.firstChild;
        searchBox.parentNode.insertBefore(actionsMenu, searchBox.nextSibling);

        // Add collection modal
        const modalHtml = `
            <div class="modal fade" id="collectionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Add to Collection</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div id="selectedItems" class="mb-3">
                                <h6>Selected Items:</h6>
                                <div id="selectedItemsList" class="border rounded p-2"></div>
                            </div>
                            <div class="collections-section">
                                <h6>Choose Collection:</h6>
                                <div id="collectionsListContainer" class="border rounded p-2"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    // Reset filters button
    document.getElementById('resetFilters')?.addEventListener('click', () => {
        console.log('Resetting all filters');
        filterIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.value = '';
            }
        });
        if (searchInput.value.trim()) {
            performSearch();
        }
    });


    function updateVisibleFilters(category) {
        document.getElementById('studyFilters').style.display =
            (category === 'all' || category === 'studies') ? 'block' : 'none';
        document.getElementById('indicationFilters').style.display =
            (category === 'all' || category === 'indications') ? 'block' : 'none';
        document.getElementById('procedureFilters').style.display =
            (category === 'all' || category === 'procedures') ? 'block' : 'none';
    }
    // Initialize
    updateVisibleFilters(currentCategory);
    setInitialFiltersFromURL();

    // Add event listener for save button
    document.getElementById('saveSearchButton')?.addEventListener('click', saveCurrentSearch);

    function setInitialFiltersFromURL() {
        const urlParams = new URLSearchParams(window.location.search);

        // Set search query if present and handle multiple terms
        const query = urlParams.get('q');
        if (query) {
            searchInput.value = query; // Set the first term in the search input

        }

        const category = urlParams.get('category');
        if (category) {
            const categoryButton = document.querySelector(`button[data-category="${category}"]`);
            if (categoryButton) {
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                categoryButton.classList.add('active');
                currentCategory = category;
            }
        }

        // If we have a query, perform the search
        if (query) {
            performSearch();
        }
    }

    function getAuthToken() {
        return localStorage.getItem('auth_token');
    }

    function getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        const token = getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    async function saveCurrentSearch() {
        const query = searchInput.value.trim();
        try {
            const response = await fetch('/api/search-history', {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({
                    query: query,
                    category: currentCategory,
                    results_count: document.querySelectorAll('.search-result-item').length,
                    is_saved: true
                })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/auth/login?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success alert-dismissible fade show';
                alertDiv.innerHTML = `
                    Search saved successfully!
                    <a href="/saved-searches">View Saved Searches</a>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                document.querySelector('.search-container').insertBefore(alertDiv, document.querySelector('.search-box-container'));

                setTimeout(() => {
                    alertDiv.remove();
                }, 5000);
            }
        } catch (error) {
            console.error('Error saving search:', error);
            alert('Failed to save search. Please try again.');
        }
    }



    window.showCreateCollectionForm = function() {
        document.getElementById('collectionsListView').style.display = 'none';
        document.getElementById('createCollectionForm').style.display = 'block';
    };

    window.showCollectionsList = function() {
        document.getElementById('createCollectionForm').style.display = 'none';
        document.getElementById('collectionsListView').style.display = 'block';
    };

    window.createNewCollection = async function(event) {
        event.preventDefault();

        const title = document.getElementById('collectionTitle').value.trim();
        const description = document.getElementById('collectionDescription').value.trim();

        if (!title) {
            showError('Title is required');
            return;
        }

        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                window.location.href = '/auth/login?next=/collections';
                return;
            }

            const response = await fetch('/api/collections', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    description: description || null
                })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/auth/login?next=/collections';
                    return;
                }
                const error = await response.json();
                throw new Error(error.detail || 'Failed to create collection');
            }

            const collection = await response.json();

            // Reset form
            document.getElementById('collectionTitle').value = '';
            document.getElementById('collectionDescription').value = '';

            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('collectionModal'));
            if (modal) {
                modal.hide();
            }

            // Show success message
            showSuccess('Collection created successfully');

            // Reload collections list
            setTimeout(() => {
                loadCollections();
                showCollectionsList();
            }, 500);

        } catch (error) {
            console.error('Error creating collection:', error);
            showError(error.message || 'Failed to create collection. Please try again.');
        }
    };

    const collectionModal = `
        <div class="modal fade" id="collectionModal" tabindex="-1" aria-labelledby="collectionModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="collectionModalLabel">Add to Collection</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div><div class="modal-body">
                        <!-- Collections List View -->
                        <div id="collectionsListView">
                            <div id="collectionsListContainer">
                                Loading collections...
                            </div>
                            <div class="mt-3">
                                <button type="button" class="btn btn-primary" onclick="window.showCreateCollectionForm()">
                                    Create New Collection
                                </button>
                            </div>
                        </div>

                        <!-- Create Collection Form -->
                        <div id="createCollectionForm" style="display: none;">
                            <form onsubmit="window.createNewCollection(event)">
                                <div class="mb-3">
                                    <label for="collectionTitle" class="form-label">Collection Title</label>
                                    <input type="text" class="form-control" id="collectionTitle" required>
                                </div>
                                <div class="mb3:                                    <label for="collectionDescription" class="form-label">Description</label>
                                    <textarea class="form-control" id="collectionDescription" rows="3"></textarea>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <button type="button" class="btn btn-secondary" onclick="window.showCollectionsList()">
                                        Back to Collections
                                    </button>
                                    <button type="submit" class="btn btn-primary">Create Collection</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove any existing modal
    const existingModal = document.getElementById('collectionModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add the updated modal
    document.body.insertAdjacentHTML('beforeend', collectionModal);

    // Add event handler for "Add to Collection" menu item
    document.getElementById('addToCollectionMenuItem')?.addEventListener('click', () => {
        const modal = new bootstrap.Modal(document.getElementById('collectionModal'));
        loadCollections();
        updateSelectedItemsList();
        modal.show();
    });

    async function loadCollections() {
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                window.location.href = '/auth/login?next=/collections';
                return;
            }

            const response = await fetch('/api/collections', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch collections');
            }

            const collections = await response.json();
            const container = document.getElementById('collectionsListContainer');
            if (!container) return;

            if (collections.length === 0) {
                container.innerHTML = '<p>No collections yet. Create your first collection.</p>';
            } else {
                container.innerHTML = collections.map(collection => `
                    <div class="collection-option mb-2">
                        <button class="btn btn-outline-secondary w-100 text-start"
                                onclick="addToCollection(${collection.id})">
                            ${collection.title}
                            <small class="d-block text-muted">${collection.description || ''}</small>
                        </button>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading collections:', error);
            showError('Failed to load collections');
        }
    }

    async function addToCollection(collectionId) {
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                window.location.href = '/auth/login?next=/collections';
                return;
            }

            const checkedProducts = document.querySelectorAll('.form-check-input:checked');
            const dataProductIds = Array.from(checkedProducts).map(checkbox => {
                const dataProduct = checkbox.closest('.data-product-item').dataset.productId;
                return parseInt(dataProduct, 10);
            });

            if (dataProductIds.length === 0) {
                showError('Please select at least one data product');
                return;
            }

            const response = await fetch(`/api/collections/${collectionId}/items`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ data_product_ids: dataProductIds })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to add items to collection');
            }

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('collectionModal'));
            if (modal) {
                modal.hide();
            }

            // Clear checkboxes
            checkedProducts.forEach(checkbox => checkbox.checked = false);
            updateMenuVisibility();

            showSuccess('Items added to collection successfully');
        } catch (error) {
            console.error('Error adding items to collection:', error);
            showError(error.message || 'Failed to add items to collection. Please try again.');
        }
    }
    searchInput?.addEventListener('input',debounceSearch);
});