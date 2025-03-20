from flask import Blueprint, render_template, redirect, url_for
import json
from flask import request, jsonify
from datetime import datetime
from flask import session, flash
import sqlite3


# Blueprint setup for main application route handling
main = Blueprint('main', __name__)


# Establishing connection to database, creating tables if they don't exist
def setup_database():
    with sqlite3.connect('instance/iescp.db') as conn:
        # USER table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'sponsor', 'influencer')),
                name TEXT,
                category TEXT,
                niche TEXT,
                reach INTEGER,
                flagged BOOLEAN DEFAULT FALSE
            )
        ''')
        # CAMPAIGN table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS campaign (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                visibility TEXT NOT NULL CHECK(visibility IN ('public', 'private')),
                goals TEXT,
                category TEXT,
                niche TEXT
            )
        ''')
        # AD REQUEST table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ad_request (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                influencer_id INTEGER,
                message TEXT,
                requirements TEXT,
                payment_amount REAL,
                status TEXT NOT NULL CHECK(status IN ('Pending', 'Accepted', 'Rejected', 'Negotiating')),
                FOREIGN KEY (campaign_id) REFERENCES campaign(id),
                FOREIGN KEY (influencer_id) REFERENCES user(id)
            )
        ''')
        conn.commit()


@main.before_app_request
def setup():
    setup_database()

# Home page/Landing page
@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html')

# Sign up page
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password != confirm_password:
            flash('Oops! Your passwords don\'t match. Please try again!', 'danger')
            return redirect(url_for('main.signup'))

        if role not in ['admin', 'influencer', 'sponsor']:
            flash('Selected role is not valid. Please choose a correct role!', 'danger')
            return redirect(url_for('main.signup'))

        try:
            with sqlite3.connect('instance/iescp.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user (username, email, password, role)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, password, role))
                conn.commit()
            flash('Your account has been created successfully! Please log in to continue.', 'success')
            return redirect(url_for('main.login'))
        except sqlite3.IntegrityError:
            flash('This username or email is already in use. Please choose another!', 'danger')
            return redirect(url_for('main.signup'))

    return render_template('signup.html')


# Login page
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user WHERE username = ? AND password = ? AND role = ?
            ''', (username, password, role))
            user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            if role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            elif role == 'sponsor':
                return redirect(url_for('main.sponsor_dashboard'))
            elif role == 'influencer':
                return redirect(url_for('main.influencer_dashboard'))
        else:
            flash('Invalid username, password, or role. Please try again!', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html')



# Logout
@main.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have successfully logged out. Come back soon!', 'success')
    return redirect(url_for('main.home'))




# Lists of categories and niches, that are made GLOBALLY accessible so that any user can access these
categories = [
    'Business', 'Education', 'Entertainment', 'Fashion', 'Fitness', 'Food', 'Gaming', 'Health', 'Lifestyle', 'Music', 'Photography', 
    'Politics', 'Sports', 'Technology', 'Travel'
]
niches = [
    'Cloud Computing', 'Complete Web Development Bootcamp', 'Cosplay', 'Cryptocurrency', 'Cybersecurity', 'DIY Projects', 
    'Eco-Friendly Travel', 'Freelance Business', 'Gadget Reviews', 'Historical Tours', 'Home Workouts', 'Indie Music', 
    'Internet of Things (IoT)', 'Luxury Fashion', 'Minimalist Living', 'Organic Beauty', 'Personal Finance', 'Vegan Lifestyle', 
    'Winter Sports Holidays', 'Yoga and Meditation'
]






# Admin dashboard page
@main.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('You must be an ADMIN to access this page!', 'danger')
        return redirect(url_for('main.login'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        
        # Fetching admin's name
        cursor.execute('''
            SELECT username FROM user WHERE id = ? AND role = 'admin'
        ''', (session.get('user_id'),))
        admin_name = cursor.fetchone()
        admin_name = admin_name[0] if admin_name else 'Unknown'


        # Counting all active users existing in the database
        cursor.execute('SELECT COUNT(*) FROM user')
        active_users_count = cursor.fetchone()[0]

        # Counting Flagged entities
        # Flagged users
        cursor.execute('SELECT COUNT(*) FROM user WHERE flagged = TRUE')
        flagged_users_count = cursor.fetchone()[0]
        # Flagged campaigns
        cursor.execute('SELECT COUNT(*) FROM campaign WHERE flagged = TRUE')
        flagged_campaigns_count = cursor.fetchone()[0]

        # Counting active campaigns
        cursor.execute('SELECT COUNT(*) FROM campaign')
        active_campaigns_count = cursor.fetchone()[0]
        # Counting public campaigns
        cursor.execute('SELECT COUNT(*) FROM campaign where visibility="Public"')
        public_campaigns_count = cursor.fetchone()[0]
        # Counting private campaigns
        cursor.execute('SELECT COUNT(*) FROM campaign where visibility="Private"')
        private_campaigns_count = cursor.fetchone()[0]
        

        # Counting ad requests based on their statuses - pending/accepted/rejected
        cursor.execute('SELECT COUNT(*) FROM ad_request WHERE status = "Pending"')
        pending_ad_requests_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM ad_request WHERE status = "Accepted"')
        accepted_ad_requests_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM ad_request WHERE status = "Rejected"')
        rejected_ad_requests_count = cursor.fetchone()[0]
        # Total ad request count
        total_ad_requests_count = pending_ad_requests_count + accepted_ad_requests_count + rejected_ad_requests_count

        ad_request_status_counts = {
            'Pending': pending_ad_requests_count,
            'Accepted': accepted_ad_requests_count,
            'Rejected': rejected_ad_requests_count
        }

        # Stats for charts in ADMIN page
        total_users = active_users_count
        total_campaigns = active_campaigns_count
        private_campaigns = private_campaigns_count 
        flagged_campaigns_count = flagged_campaigns_count  

    return render_template('admin/dashboard.html',
                           username=admin_name,
                           active_users=total_users,
                           active_campaigns=total_campaigns,
                           private_campaigns=private_campaigns,
                           ad_request_statuses=ad_request_status_counts,
                           flagged_users=flagged_users_count,
                           flagged_campaigns=flagged_campaigns_count,
                           pending_ad_requests_count=pending_ad_requests_count,
                           rejected_ad_requests_count=rejected_ad_requests_count,
                           accepted_ad_requests_count=accepted_ad_requests_count,
                           total_ad_requests=total_ad_requests_count)
    


# Charts for admin dashboard page
@main.route('/admin/charts')
def admin_charts():
    if session.get('role') != 'admin':
        flash('You must be an ADMIN to access this page!', 'danger')
        return redirect(url_for('main.login'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        
        # Stats for admin page's charts
        total_users = cursor.execute('SELECT COUNT(*) FROM user').fetchone()[0]
        total_campaigns = cursor.execute('SELECT COUNT(*) FROM campaign').fetchone()[0]
        total_ad_requests = cursor.execute('SELECT COUNT(*) FROM ad_request').fetchone()[0]
        
        active_campaigns = cursor.execute('SELECT COUNT(*) FROM campaign WHERE status = "Active"').fetchone()[0]
        inactive_campaigns = cursor.execute('SELECT COUNT(*) FROM campaign WHERE status = "Inactive"').fetchone()[0]
        
        ad_request_status_counts = cursor.execute('SELECT status, COUNT(*) FROM ad_request GROUP BY status').fetchall()
        ad_request_labels = [status for status, _ in ad_request_status_counts]
        ad_request_values = [count for _, count in ad_request_status_counts]
        
        flagged_users = cursor.execute('SELECT COUNT(*) FROM user WHERE flagged = TRUE').fetchone()[0]
        flagged_campaigns = cursor.execute('SELECT COUNT(*) FROM campaign WHERE flagged = TRUE').fetchone()[0]
        
        chart_data = {
            'active_users': total_users,
            'public_campaigns': total_campaigns,
            'private_campaigns': inactive_campaigns,
            'ad_request_statuses': {
                'labels': ad_request_labels,
                'data': ad_request_values
            },
            'flagged_users': flagged_users,
            'flagged_campaigns': flagged_campaigns
        }

    return render_template('admin/charts.html', chart_data=json.dumps(chart_data))



# Flag users page by admin
@main.route('/admin/flag_user', methods=['GET', 'POST'])
def flag_user():
    if session.get('role') != 'admin':
        flash('You must be an ADMIN to access this page!', 'danger')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            if action == 'flag':
                cursor.execute('UPDATE user SET flagged = TRUE WHERE id = ?', (user_id,))
                flash('User has been flagged', 'success')
            elif action == 'unflag':
                cursor.execute('UPDATE user SET flagged = FALSE WHERE id = ?', (user_id,))
                flash('User has been unflagged', 'success')
            elif action == 'delete':
                cursor.execute('DELETE FROM user WHERE id = ?', (user_id,))
                flash('User has been deleted', 'success')
            conn.commit()

    # Fetching users for display
    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, role, flagged FROM user')
        users = cursor.fetchall()
    
    return render_template('admin/flag_user.html', users=users)



# Flag campaigns by admin
@main.route('/admin/flag_campaign', methods=['POST'])
def flag_campaign():
    if session.get('role') != 'admin':
        flash('You must be an ADMIN to access this page!', 'danger')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        campaign_id = request.form.get('campaign_id')
        action = request.form.get('action')

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            if action == 'flag':
                cursor.execute('UPDATE campaign SET flagged = TRUE WHERE id = ?', (campaign_id,))
                flash('Campaign has been flagged', 'success')
            elif action == 'unflag':
                cursor.execute('UPDATE campaign SET flagged = FALSE WHERE id = ?', (campaign_id,))
                flash('Campaign has been unflagged', 'success')
            elif action == 'delete':
                cursor.execute('DELETE FROM campaign WHERE id = ?', (campaign_id,))
                flash('Campaign has been deleted', 'success')
            conn.commit()

    return redirect(url_for('main.view_campaigns'))



# View campaigns by admin
@main.route('/admin/view_campaigns')
def view_campaigns():
    if session.get('role') != 'admin':
        flash('You must be an ADMIN to access this page!', 'danger')
        return redirect(url_for('main.login'))

    today = datetime.now().strftime('%Y-%m-%d')

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, description, start_date, end_date, budget, visibility, goals, flagged FROM campaign')
        campaigns = cursor.fetchall()
    
    return render_template('admin/view_campaigns.html', campaigns=campaigns, today=today)



# Delete campaigns by admin user
@main.route('/admin/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    if session.get('role') != 'admin':
        flash('You must be an ADMIN to access this page!', 'danger')
        return redirect(url_for('main.login'))
    
    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM campaign WHERE id = ?', (campaign_id,))
        conn.commit()
    flash('Campaign deleted successfully', 'success')
    return redirect(url_for('main.view_campaigns'))


# View ad requests page for admin
@main.route('/admin/view_ad_requests')
def view_ad_requests():
    if session.get('role') != 'admin':
        flash('You must be an ADMIN to access this page!', 'danger')
        return redirect(url_for('main.login'))
    
    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ad_request')
        ad_requests = cursor.fetchall()
    
    return render_template('admin/view_ad_requests.html', ad_requests=ad_requests)


# Delete ad requests by admin
@main.route('/admin/delete_ad_request/<int:ad_request_id>', methods=['POST'])
def admin_delete_ad_request(ad_request_id):
    if session.get('role') != 'admin':
        flash('You must be an ADMIN to access this page!', 'danger')
        return redirect(url_for('main.login'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ad_request WHERE id = ?', (ad_request_id,))
        conn.commit()
    flash('Ad request deleted successfully', 'success')
    return redirect(url_for('main.view_ad_requests'))








# Influencer Dashboard
@main.route('/influencer/dashboard')
def influencer_dashboard():
    if session.get('role') != 'influencer':
        flash('You must be an INFLUENCER to access this page!', 'danger')
        return redirect(url_for('main.login'))

    user_id = session.get('user_id')

    if not user_id:
        flash('User is not logged in!', 'danger')
        return redirect(url_for('main.login'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()

        # Fetching influencer details
        cursor.execute('SELECT username, email, category, niche, reach FROM user WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('main.login'))

        user_data = {
            'username': user[0],
            'email': user[1],
            'category': user[2],
            'niche': user[3],
            'reach': user[4]
        }
        
        # Fetching ad requests (with sponsor names)
        cursor.execute('''
            SELECT ar.id, ar.campaign_id, ar.message, ar.requirements, ar.payment_amount, ar.status, c.name AS campaign_name, s.username AS sponsor_name
            FROM ad_request ar
            JOIN campaign c ON ar.campaign_id = c.id
            JOIN user s ON ar.sponsor_id = s.id
            WHERE ar.influencer_id = ?
        ''', (user_id,))
        ad_requests = cursor.fetchall()

        # Counting ad requests
        active_ad_requests = len([r for r in ad_requests if r[5] == 'Active'])
        pending_ad_requests = len([r for r in ad_requests if r[5] == 'Pending'])
        accepted_ad_requests = len([r for r in ad_requests if r[5] == 'Accepted'])

    return render_template(
        'influencer/dashboard.html', 
        user=user_data,
        ad_requests=ad_requests,
        active_ad_requests=active_ad_requests,
        pending_ad_requests=pending_ad_requests,
        accepted_ad_requests=accepted_ad_requests
    )



# Influencer Profile
@main.route('/influencer/profile', methods=['GET', 'POST'])
def influencer_profile():
    if session.get('role') != 'influencer':
        flash('You must be an INFLUENCER to access this page!', 'danger')
        return redirect(url_for('main.login'))

    user_id = session.get('user_id')

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        category = request.form.get('category')
        niche = request.form.get('niche')
        reach = request.form.get('reach')

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user
                SET username = ?, email = ?, category = ?, niche = ?, reach = ?
                WHERE id = ?
            ''', (username, email, category, niche, reach, user_id))
            conn.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.influencer_dashboard'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, email, category, niche, reach FROM user WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if not user:
            flash('User is not found!', 'danger')
            return redirect(url_for('main.login'))

        user_data = {
            'username': user[0],
            'email': user[1],
            'category': user[2],
            'niche': user[3],
            'reach': user[4]
        }

    return render_template('influencer/profile.html', user=user_data, categories=categories, niches=niches)


# Search campaigns by influencers
@main.route('/influencer/search_campaigns', methods=['GET', 'POST'])
def search_campaigns():
    if session.get('role') != 'influencer':
        flash('You must be an INFLUENCER to access this page!', 'danger')
        return redirect(url_for('main.login'))

    campaigns = []

    if request.method == 'POST':
        category = request.form.get('category')
        niche = request.form.get('niche')
        min_budget = request.form.get('min_budget', 0, type=int)
        max_budget = request.form.get('max_budget', 50000, type=int)

        query = '''
            SELECT * FROM campaign
            WHERE visibility = 'public'
            AND (budget BETWEEN ? AND ?)
            AND (? IS NULL OR category = ?)
            AND (? IS NULL OR niche = ?)
        '''

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            cursor.execute(query, (min_budget, max_budget, category if category else None, category if category else None, niche if niche else None, niche if niche else None))
            campaigns = cursor.fetchall()

    return render_template('influencer/search_campaigns.html', campaigns=campaigns, categories=categories, niches=niches)


# View ad requests by influencer
@main.route('/influencer/view_ad_requests')
def influencer_view_ad_requests():
    if session.get('role') != 'influencer':
        flash('You must be an INFLUENCER to access this page!', 'danger')
        return redirect(url_for('main.login'))

    user_id = session.get('user_id')

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ar.id, ar.campaign_id, ar.message, ar.requirements, ar.payment_amount, ar.status, c.name AS campaign_name, s.username AS sponsor_name
            FROM ad_request ar
            JOIN campaign c ON ar.campaign_id = c.id
            JOIN user s ON ar.sponsor_id = s.id
            WHERE ar.influencer_id = ?
        ''', (user_id,))
        ad_requests = cursor.fetchall()

    return render_template('influencer/view_ad_requests.html', ad_requests=ad_requests)



# Accept ad request by influencer
@main.route('/ad_request/accept/<int:ad_request_id>')
def accept_ad_request(ad_request_id):
    if session.get('role') != 'influencer':
        flash('You must be an INFLUENCER to access this page!', 'danger')
        return redirect(url_for('main.login'))

    user_id = session.get('user_id')

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE ad_request SET status = ? WHERE id = ? AND influencer_id = ?', ('Accepted', ad_request_id, user_id))
        conn.commit()

        cursor.execute('SELECT sponsor_id FROM ad_request WHERE id = ?', (ad_request_id,))
        sponsor_id = cursor.fetchone()[0]

    flash('Ad request accepted!', 'success')
    return redirect(url_for('main.influencer_dashboard'))


# Reject ad request by influencer
@main.route('/ad_request/reject/<int:ad_request_id>')
def reject_ad_request(ad_request_id):
    if session.get('role') != 'influencer':
        flash('You must be an INFLUENCER to access this page!', 'danger')
        return redirect(url_for('main.login'))

    user_id = session.get('user_id')

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE ad_request SET status = ? WHERE id = ? AND influencer_id = ?', ('Rejected', ad_request_id, user_id))
        conn.commit()

        cursor.execute('SELECT sponsor_id FROM ad_request WHERE id = ?', (ad_request_id,))
        sponsor_id = cursor.fetchone()[0]

    flash('Ad request rejected!', 'success')
    return redirect(url_for('main.influencer_dashboard'))


# Influencer's negotiation
@main.route('/influencer/respond_negotiation/<int:ad_request_id>', methods=['GET', 'POST'])
def respond_negotiation(ad_request_id):
    if session.get('role') != 'influencer':
        flash('You must be an INFLUENCER to access this page!', 'danger')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        action = request.form['action']
        new_payment_amount = request.form.get('payment_amount')
        response_message = request.form['message']

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()

            # Fetching current payment amount demanded by influencer
            cursor.execute('SELECT payment_amount FROM ad_request WHERE id = ?', (ad_request_id,))
            current_payment_amount = cursor.fetchone()[0]

            if action == 'accept':
                cursor.execute('''
                    UPDATE ad_request
                    SET status = 'Accepted', payment_amount = ?
                    WHERE id = ?
                ''', (new_payment_amount if new_payment_amount else current_payment_amount, ad_request_id))
                flash('Ad request accepted!', 'success')

            elif action == 'reject':
                cursor.execute('''
                    UPDATE ad_request
                    SET status = 'Rejected'
                    WHERE id = ?
                ''', (ad_request_id,))
                flash('Ad request rejected!', 'success')

            elif action == 'negotiate':
                # Retrieving existing message
                cursor.execute('SELECT message FROM ad_request WHERE id = ?', (ad_request_id,))
                existing_message = cursor.fetchone()[0] or ''

                # Appending the new message
                updated_message = existing_message + "<br>" + "<br>" + f"{response_message}"

                cursor.execute('''
                    UPDATE ad_request
                    SET status = 'Negotiating', message = ?, payment_amount = ?
                    WHERE id = ?
                ''', (updated_message, new_payment_amount if new_payment_amount else current_payment_amount, ad_request_id))
                flash('Negotiation sent to sponsor!', 'success')

            conn.commit()

            cursor.execute('SELECT sponsor_id FROM ad_request WHERE id = ?', (ad_request_id,))
            sponsor_id = cursor.fetchone()[0]
            return redirect(url_for('main.influencer_dashboard'))

    return render_template('influencer/respond_negotiation.html', ad_request_id=ad_request_id)






# Sponsor Dashboard Route
@main.route('/sponsor/dashboard')
def sponsor_dashboard():
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))

    sponsor_id = session['user_id']

    with sqlite3.connect('instance/iescp.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetching sponsor name
        cursor.execute('''
            SELECT username FROM user WHERE id = ? AND role = 'sponsor'
        ''', (sponsor_id,))
        sponsor_name = cursor.fetchone()
        sponsor_name = sponsor_name['username'] if sponsor_name else 'Unknown'

        # Fetching campaign stats
        cursor.execute('''
            SELECT COUNT(*) AS total_campaigns FROM campaign WHERE sponsor_id = ?
        ''', (sponsor_id,))
        total_campaigns = cursor.fetchone()['total_campaigns']

        cursor.execute('''
            SELECT COUNT(*) AS active_campaigns FROM campaign WHERE sponsor_id = ? AND start_date <= DATE('now') AND end_date >= DATE('now')
        ''', (sponsor_id,))
        active_campaigns = cursor.fetchone()['active_campaigns']

        cursor.execute('''
            SELECT COUNT(*) AS expired_campaigns FROM campaign WHERE sponsor_id = ? AND end_date < DATE('now')
        ''', (sponsor_id,))
        expired_campaigns = cursor.fetchone()['expired_campaigns']
        
        cursor.execute('''
            SELECT COUNT(*) AS upcoming_campaigns FROM campaign 
            WHERE sponsor_id = ? AND start_date > DATE('now')
        ''', (sponsor_id,))
        upcoming_campaigns = cursor.fetchone()['upcoming_campaigns']

        # Fetching ad requests stats
        cursor.execute('''
            SELECT COUNT(*) AS total_ad_requests FROM ad_request WHERE sponsor_id = ?
        ''', (sponsor_id,))
        total_ad_requests = cursor.fetchone()['total_ad_requests']

        cursor.execute('''
            SELECT status, COUNT(*) AS count FROM ad_request WHERE sponsor_id = ? GROUP BY status
        ''', (sponsor_id,))
        ad_request_stats = cursor.fetchall()
        ad_request_stats_dict = {row['status']: row['count'] for row in ad_request_stats}

        # Ensuring all ad request statuses are included
        for status in ['Pending', 'Accepted', 'Rejected', 'Negotiating']:
            if status not in ad_request_stats_dict:
                ad_request_stats_dict[status] = 0

        # Fetching campaigns created by sponsor
        cursor.execute('''
            SELECT id, name, description, start_date, end_date,
                   CASE
                       WHEN start_date > DATE('now') THEN 'Upcoming'
                       WHEN end_date < DATE('now') THEN 'Expired'
                       ELSE 'Active'
                   END AS status,
                   flagged, category, niche
            FROM campaign
            WHERE sponsor_id = ?
        ''', (sponsor_id,))
        campaigns = cursor.fetchall()

        # Fetching ad requests for sponsor
        cursor.execute('''
            SELECT ad_request.id, ad_request.campaign_id, ad_request.influencer_id, ad_request.message, ad_request.requirements, ad_request.payment_amount, ad_request.status, campaign.name, user.username
            FROM ad_request
            JOIN campaign ON ad_request.campaign_id = campaign.id
            JOIN user ON ad_request.influencer_id = user.id
            WHERE ad_request.sponsor_id = ?
        ''', (sponsor_id,))
        ad_requests = cursor.fetchall()

    # Converting ad_request_stats_dict to lists for chart shown in sponsor dashboard
    ad_request_labels = ['Pending', 'Accepted', 'Rejected', 'Negotiating']
    ad_request_values = [ad_request_stats_dict.get(label, 0) for label in ad_request_labels]

    return render_template('sponsor/dashboard.html', 
                           username=sponsor_name, 
                           total_campaigns=total_campaigns, 
                           active_campaigns=active_campaigns, 
                           expired_campaigns=expired_campaigns,
                           upcoming_campaigns=upcoming_campaigns, 
                           total_ad_requests=total_ad_requests,
                           campaigns=campaigns,
                           ad_requests=ad_requests,
                           ad_request_labels=ad_request_labels,
                           ad_request_values=ad_request_values)


# Create campaign by sponsor
@main.route('/sponsor/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form['budget']
        visibility = request.form['visibility']
        goals = request.form['goals']
        category = request.form['category']
        niche = request.form['niche']
        sponsor_id = session['user_id']

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO campaign (name, description, start_date, end_date, budget, visibility, goals, category, niche, sponsor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, start_date, end_date, budget, visibility, goals, category, niche, sponsor_id))
            conn.commit()
            flash('Campaign created successfully', 'success')
            return redirect(url_for('main.sponsor_dashboard'))

    return render_template('sponsor/create_campaign.html', categories=categories, niches=niches)


# Edit/update campaign details
@main.route('/sponsor/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form['budget']
        visibility = request.form['visibility']
        goals = request.form['goals']
        category = request.form['category']
        niche = request.form['niche']

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE campaign
                SET name = ?, description = ?, start_date = ?, end_date = ?, budget = ?, visibility = ?, goals = ?, category = ?, niche = ?
                WHERE id = ?
            ''', (name, description, start_date, end_date, budget, visibility, goals, category, niche, campaign_id))
            conn.commit()
            flash('Campaign updated successfully!', 'success')
            return redirect(url_for('main.sponsor_dashboard'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM campaign WHERE id = ?', (campaign_id,))
        campaign = cursor.fetchone()

    if not campaign:
        flash('Campaign not found!', 'danger')
        return redirect(url_for('main.sponsor_dashboard'))

    campaign_dict = {
        'id': campaign[0],
        'name': campaign[1],
        'description': campaign[2],
        'start_date': campaign[3],
        'end_date': campaign[4],
        'budget': campaign[5],
        'visibility': campaign[6],
        'goals': campaign[7],
        'category': campaign[8],
        'niche': campaign[9]
    }

    return render_template('sponsor/edit_campaign.html', 
                           campaign=campaign_dict, 
                           categories=categories, 
                           niches=niches)


# Delete campaign by sponsor
@main.route('/sponsor/delete_campaign/<int:campaign_id>')
def delete_campaigns(campaign_id):
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM campaign
            WHERE id = ? AND sponsor_id = ?
        ''', (campaign_id, session['user_id']))
        conn.commit()
        flash('Campaign deleted successfully', 'success')
    
    return redirect(url_for('main.sponsor_dashboard'))


# View ad requests by sponsor
@main.route('/sponsor/view_ad_requests')
def sponsor_view_ad_requests():
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))
    
    sponsor_id = session['user_id']

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ad_request.id, ad_request.campaign_id, ad_request.influencer_id, ad_request.message, ad_request.requirements, ad_request.payment_amount, ad_request.status, campaign.name, user.username
            FROM ad_request
            JOIN campaign ON ad_request.campaign_id = campaign.id
            JOIN user ON ad_request.influencer_id = user.id
            WHERE campaign.sponsor_id = ?
        ''', (sponsor_id,))
        ad_requests = cursor.fetchall()

    return render_template('sponsor/view_ad_requests.html', ad_requests=ad_requests)



# Create ad request by sponsor
@main.route('/sponsor/create_ad_request', methods=['GET', 'POST'])
def create_ad_request():
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        campaign_id = request.form.get('campaign_id', None)
        influencer_id = request.form.get('influencer_id', None)
        requirements = request.form.get('requirements', '')
        payment_amount = request.form.get('payment_amount', None)
        status = 'Pending'
        sponsor_id = session.get('user_id')
        message = request.form.get('messages', '')

        if not all([campaign_id, influencer_id, payment_amount]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.create_ad_request'))

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ad_request (campaign_id, influencer_id, message, requirements, payment_amount, status, sponsor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (campaign_id, influencer_id, message, requirements, payment_amount, status, sponsor_id))
            conn.commit()
            flash('Ad request created successfully!', 'success')
            return redirect(url_for('main.sponsor_dashboard'))

    # Fetching campaigns & influencers for dropdowns
    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM campaign WHERE sponsor_id = ?', (session.get('user_id'),))
        campaigns = cursor.fetchall()
        cursor.execute('SELECT id, username FROM user WHERE role = "influencer"')
        influencers = cursor.fetchall()

    return render_template('sponsor/create_ad_request.html', campaigns=campaigns, influencers=influencers)



# Edit/update ad request by sponsor
@main.route('/sponsor/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def edit_ad_request(ad_request_id):
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        campaign_id = request.form['campaign_id']
        influencer_id = request.form['influencer_id']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        status = request.form['status']
        message = request.form['message']

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE ad_request
                SET campaign_id = ?, influencer_id = ?, message = ?, requirements = ?, payment_amount = ?, status = ?
                WHERE id = ?
            ''', (campaign_id, influencer_id, message, requirements, payment_amount, status, ad_request_id))
            conn.commit()
            flash('Ad request updated successfully!', 'success')
            return redirect(url_for('main.sponsor_view_ad_requests'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ad_request WHERE id = ?', (ad_request_id,))
        ad_request = cursor.fetchone()

    if not ad_request:
        flash('Ad request not found!', 'danger')
        return redirect(url_for('main.sponsor_view_ad_requests'))

    # Converting tuple to dictionary
    ad_request_dict = {
        'id': ad_request[0],
        'campaign_id': ad_request[1],
        'influencer_id': ad_request[2],
        'message': ad_request[3],
        'requirements': ad_request[4],
        'payment_amount': ad_request[5],
        'status': ad_request[6]
    }

    # Fetching campaigns & influencers for dropdowns
    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM campaign WHERE sponsor_id = ?', (session['user_id'],))
        campaigns = cursor.fetchall()
        cursor.execute('SELECT id, username FROM user WHERE role = "influencer"')
        influencers = cursor.fetchall()

    return render_template('sponsor/update_ad_request.html', ad_request=ad_request_dict, campaigns=campaigns, influencers=influencers)



# Sponsor's negotiation ad request
@main.route('/sponsor/negotiation/<int:ad_request_id>', methods=['GET', 'POST'])
def sponsor_negotiation(ad_request_id):
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        new_payment_amount = request.form.get('payment_amount')
        response_message = request.form.get('response_message', '')

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()

            # Fetching current payment amount
            cursor.execute('SELECT payment_amount FROM ad_request WHERE id = ?', (ad_request_id,))
            current_payment_amount = cursor.fetchone()[0]

            # Updating ad request status & payment amount
            cursor.execute('''
                UPDATE ad_request
                SET status = 'Negotiating', payment_amount = ?
                WHERE id = ?
            ''', (new_payment_amount if new_payment_amount else current_payment_amount, ad_request_id))

            # Appending message to the same ad request
            try:
                cursor.execute('SELECT message FROM ad_request WHERE id = ?', (ad_request_id,))
                existing_message = cursor.fetchone()[0] or ''
                updated_message = existing_message + "<br>" + "<br>" + f"{response_message}"
                print(f"Appending message: {updated_message}")
                
                cursor.execute('UPDATE ad_request SET message = ? WHERE id = ?', (updated_message, ad_request_id))
                conn.commit()
                flash('Negotiation sent to influencer', 'success')
            except sqlite3.OperationalError as e:
                print(f"OperationalError: {e}")
                flash('An error occurred while processing the request!', 'danger')

            return redirect(url_for('main.sponsor_view_ad_requests'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ad_request WHERE id = ?', (ad_request_id,))
        ad_request = cursor.fetchone()

        if not ad_request:
            flash('Ad request not found!', 'danger')
            return redirect(url_for('main.sponsor_view_ad_requests'))

        ad_request_dict = {
            'id': ad_request[0],
            'campaign_id': ad_request[1],
            'influencer_id': ad_request[2],
            'status': ad_request[3],
            'payment_amount': ad_request[4] or '',
            'message': ad_request[5] or '',
            'response_message': ad_request[6] or ''
        }

    return render_template('sponsor/negotiation.html', ad_request=ad_request_dict)


# Deleting ad request by sponsor
@main.route('/sponsor/delete_ad_request/<int:ad_request_id>')
def delete_ad_request(ad_request_id):
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))

    with sqlite3.connect('instance/iescp.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM ad_request
            WHERE id = ? AND EXISTS (
                SELECT 1 FROM campaign WHERE id = ad_request.campaign_id AND sponsor_id = ?
            )
        ''', (ad_request_id, session['user_id']))
        conn.commit()
        flash('Ad request deleted successfully!', 'success')

    return redirect(url_for('main.sponsor_view_ad_requests'))


# Search influencers by sponsors
@main.route('/sponsor/search_influencers', methods=['GET', 'POST'])
def search_influencers():
    if session.get('role') != 'sponsor':
        flash('You must be a SPONSOR to access this page!', 'danger')
        return redirect(url_for('main.login'))
    
    influencers = []
    if request.method == 'POST':
        search_category = request.form.get('category')
        search_niche = request.form.get('niche')
        search_reach = request.form.get('reach')

        query = '''
            SELECT id, username, email, category, niche, reach 
            FROM user 
            WHERE role = "influencer"
        '''
        params = []

        if search_category:
            query += ' AND category = ?'
            params.append(search_category)
        if search_niche:
            query += ' AND niche = ?'
            params.append(search_niche)
        if search_reach:
            query += ' AND reach >= ?'
            params.append(search_reach)

        with sqlite3.connect('instance/iescp.db') as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            influencers = cursor.fetchall()

    return render_template('sponsor/search_influencers.html', influencers=influencers, categories=categories, niches=niches)
