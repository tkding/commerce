# eBay-like E-Commerce Auction Site

## Functionality

The eBay-like e-commerce auction site allows users to perform the following actions:

### 1. Create Listing

Users can create a new auction listing with the following details:
- Title: The title of the listing.
- Description: A text-based description of the item being listed.
- Starting Bid: The initial bid price for the item.
- Image (Optional): Users can provide a URL for an image of the item.
- Category (Optional): Users can select a category for the listing, such as Fashion, Toys, Electronics, Home, etc.

### 2. Active Listings Page

The default route of the website displays all currently active auction listings. For each listing, the following details are shown:
- Title: The title of the listing.
- Description: A brief description of the item.
- Current Price: The current highest bid on the listing.
- Photo (If available): An image of the item, if provided by the user.

### 3. Listing Page

Clicking on a listing takes users to a dedicated page for that listing, where they can view all the details about the item, including:
- Title: The title of the listing.
- Description: The complete description of the item.
- Current Price: The current highest bid on the listing.
- Watchlist: Signed-in users can add the item to their watchlist or remove it if already added.
- Bid: Signed-in users can place a bid on the item. The bid must be at least the starting bid and higher than any previous bids.
- Close Auction: If the user who created the listing is signed in, they have the option to "close" the auction, declaring the highest bidder as the winner and making the listing inactive.
- Auction Result: If the auction is closed and the signed-in user has won the auction, a message indicating their victory is displayed.
- Comments: Users can add comments to the listing page, and all comments are visible.

### 4. Watchlist

Signed-in users have access to a Watchlist page displaying all the listings they have added to their watchlist. Clicking on any listing takes the user to the specific listing page.

### 5. Categories

Users can visit a page that displays a list of all listing categories. Clicking on the name of any category shows all the active listings in that category.

### 6. Django Admin Interface

Via the Django admin interface, site administrators have the ability to view, add, edit, and delete any listings, comments, and bids made on the site.
