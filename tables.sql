CREATE TABLE users (
	id 			serial	PRIMARY KEY,
	password	text,
	email		text 	UNIQUE,
	name		text	UNIQUE,
	gender		text,
	posts		int	default 0,
	followers	int	default 0,
	followings	int	default 0
);

CREATE TABLE posts (
	id			serial	PRIMARY KEY,
	user_id		int	REFERENCES users,
	repost_id	int	REFERENCES posts,
	content		text 	not null,
	liked		int	default 0,
	create_at	timestamp	NOT NULL DEFAULT CURRENT_TIMESTAMP(0)
);

CREATE TABLE comments (
	id			serial	PRIMARY KEY,
	user_id		int	REFERENCES users,
	post_id		int	REFERENCES posts	 ON DELETE CASCADE,
	comment_id	int	REFERENCES comments	 ON DELETE CASCADE,
	content		text not null,
	create_at	timestamp	NOT NULL DEFAULT CURRENT_TIMESTAMP(0)
);

CREATE TABLE follows (
	user_id		int	REFERENCES users,
	fan_id		int	REFERENCES users,
	UNIQUE(user_id,fan_id)
);

CREATE TABLE favorates (
	user_id		int	REFERENCES users,
	post_id		int	REFERENCES posts	 ON DELETE CASCADE,
	create_at	timestamp	NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
	UNIQUE(user_id,post_id)
);

CREATE TABLE likeposts (
	user_id		int	REFERENCES users,
	post_id		int	REFERENCES posts	ON DELETE CASCADE,
	UNIQUE(user_id,post_id)
);

CREATE TABLE likecmts (
	user_id		int	REFERENCES users,
	comment_id	int	REFERENCES comments	ON DELETE CASCADE,
	UNIQUE(user_id,comment_id)
);


CREATE FUNCTION post_count() RETURNS TRIGGER AS $post_table$
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			UPDATE users SET posts=posts+1 WHERE id=new.user_id;
			RETURN NEW;
		ELSIF (TG_OP = 'DELETE') THEN
			UPDATE users SET posts=posts-1 WHERE id=old.user_id;
			RETURN NEW;
		END IF;
	END;
$post_table$ LANGUAGE plpgsql;

CREATE TRIGGER posts_counter AFTER INSERT OR DELETE ON posts
FOR EACH ROW EXECUTE PROCEDURE post_count();




CREATE FUNCTION like_post_count() RETURNS TRIGGER AS $likeposts_table$
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			UPDATE posts SET liked=liked+1 WHERE id=new.post_id;
			RETURN NEW;
		ELSIF (TG_OP = 'DELETE') THEN
			UPDATE posts SET liked=liked-1 WHERE id=old.post_id;
			RETURN OLD;
		END IF;
	END;
$likeposts_table$ LANGUAGE plpgsql;

CREATE TRIGGER like_post_counter AFTER INSERT OR DELETE ON likeposts
FOR EACH ROW EXECUTE PROCEDURE like_post_count();




CREATE FUNCTION follows_count() RETURNS TRIGGER AS $follows_table$
	BEGIN
		IF (TG_OP = 'INSERT') THEN
			UPDATE users SET followers=followers+1 WHERE id=new.user_id;
			UPDATE users SET followings=followings+1 WHERE id=new.fan_id;
			RETURN NEW;
		ELSIF (TG_OP = 'DELETE') THEN
			UPDATE users SET followers=followers-1 WHERE id=old.user_id;
			UPDATE users SET followings=followings-1 WHERE id=old.fan_id;
			RETURN OLD;
		END IF;
	END;
$follows_table$ LANGUAGE plpgsql;

CREATE TRIGGER follows_counter AFTER INSERT OR DELETE ON follows
FOR EACH ROW EXECUTE PROCEDURE follows_count();
