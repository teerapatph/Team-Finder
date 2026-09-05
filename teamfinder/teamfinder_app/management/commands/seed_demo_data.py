from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from teamfinder_app.models import (
    UserProfile, Faculty, Major, FacultyTag, MajorTag,
    Post, RecruitPost, ResultPost, Requirement, Request,
    Team, TeamMember, Feedback, PostComment
)
from chat.models import ChatGroup, GroupMessage
from taggit.models import Tag

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with rich demo data for interactive portfolio showcase"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding interactive demo data..."))

        # 1. Create Faculties and Majors
        faculties_data = [
            ("Engineering", "engineering"),
            ("Architecture & Design", "architecture-design"),
            ("Science", "science"),
            ("Commerce & Accountancy", "commerce-accountancy"),
        ]
        faculties = {}
        for name, slug in faculties_data:
            fac, _ = Faculty.objects.get_or_create(name=name, slug=slug, defaults={"faculty": name})
            faculties[name] = fac

        majors_data = [
            ("Software Engineering", "software-engineering"),
            ("Computer Engineering", "computer-engineering"),
            ("UI/UX Design", "ui-ux-design"),
            ("Data Science & AI", "data-science-ai"),
            ("Business Administration", "business-administration"),
        ]
        majors = {}
        for name, slug in majors_data:
            maj, _ = Major.objects.get_or_create(name=name, slug=slug, defaults={"major": name})
            majors[name] = maj

        # 2. Create Demo Users
        users_config = [
            {
                "username": "alex_lead",
                "password": "password123",
                "name": "Alex Chen",
                "faculty": "Engineering",
                "major": "Software Engineering",
                "year": 3,
                "bio": "Full-stack developer & Team Lead. Passionate about Hackathons, AI pipelines, and clean architectures.",
                "is_staff": False,
            },
            {
                "username": "sarah_app",
                "password": "password123",
                "name": "Sarah Jenkins",
                "faculty": "Architecture & Design",
                "major": "UI/UX Design",
                "year": 2,
                "bio": "Product designer specializing in mobile UI/UX, micro-interactions, and Figma design systems.",
                "is_staff": False,
            },
            {
                "username": "david_ai",
                "password": "password123",
                "name": "David Kim",
                "faculty": "Science",
                "major": "Data Science & AI",
                "year": 4,
                "bio": "ML engineer with focus on computer vision and real-time sensor analytics.",
                "is_staff": False,
            },
            {
                "username": "admin",
                "password": "password123",
                "name": "System Administrator",
                "faculty": "Engineering",
                "major": "Computer Engineering",
                "year": 4,
                "bio": "System Administrator account with access to all moderation tools and admin console.",
                "is_staff": True,
            }
        ]

        users = {}
        for udata in users_config:
            username = udata["username"]
            user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create_user(
                    username=username,
                    password=udata["password"],
                    name=udata["name"],
                    faculty=udata["faculty"],
                    major=udata["major"],
                    year=udata["year"],
                    email_address=f"{username}@demo.com"
                )
                if udata["is_staff"]:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
            else:
                user.name = udata["name"]
                user.faculty = udata["faculty"]
                user.major = udata["major"]
                user.year = udata["year"]
                user.save()

            UserProfile.objects.get_or_create(
                user=user,
                defaults={"bio": udata["bio"]}
            )
            users[username] = user

        alex = users["alex_lead"]
        sarah = users["sarah_app"]
        david = users["david_ai"]

        # 3. Create Project 1: Alex's AI HealthTech Hackathon
        post1, _ = Post.objects.get_or_create(
            heading="AI HealthTech Hackathon 2025 — Seeking UI/UX Designer & Data Analyst",
            defaults={
                "user": alex,
                "content": (
                    "We are developing an intelligent telemedicine triage assistant for the National HealthTech Hackathon.\n"
                    "Our backend services, LLM reasoning pipeline, and FHIR data models are already operational. "
                    "We are currently looking for a creative UI/UX designer to craft an intuitive mobile web experience for patients and clinic staff."
                ),
                "finish": False,
            }
        )
        recruit1, _ = RecruitPost.objects.get_or_create(post=post1, defaults={"status": True})
        recruit1.tag.add("AI", "HealthTech", "Hackathon", "Telemedicine")

        req1, _ = Requirement.objects.get_or_create(
            post=recruit1,
            defaults={
                "year_min": 1,
                "year_max": 4,
                "description": "Experience with Figma, user journeys, responsive web design, and wireframing."
            }
        )
        req1.req_faculty.add(faculties["Architecture & Design"], faculties["Science"])
        req1.req_major.add(majors["UI/UX Design"], majors["Data Science & AI"])

        team1, _ = Team.objects.get_or_create(recruit_post=post1, defaults={"team_leader": alex})
        TeamMember.objects.get_or_create(team=team1, member=alex)

        chat1, _ = ChatGroup.objects.get_or_create(team=team1, defaults={"admin": alex, "is_private": False})
        chat1.members.add(alex)

        # Pending join request from Sarah to Alex's project (so visitors can test accepting requests)
        req_sarah, _ = Request.objects.get_or_create(
            post=post1,
            user=sarah,
            requirement=req1,
            defaults={
                "message": "Hi Alex! I'm a 2nd year UI/UX Design student. I've designed several health and wellness mobile flows in Figma and would love to collaborate on the triage interface!"
            }
        )

        # 4. Create Project 2: David's Campus Shuttle Tracker
        post2, _ = Post.objects.get_or_create(
            heading="Campus Shuttle Tracker & Smart Route Finder",
            defaults={
                "user": david,
                "content": (
                    "Developing a real-time shuttle bus arrival tracking web application for campus commuters. "
                    "Integrates with GPS tracker nodes, estimated wait time predictions, and automated bus schedules."
                ),
                "finish": False,
            }
        )
        recruit2, _ = RecruitPost.objects.get_or_create(post=post2, defaults={"status": True})
        recruit2.tag.add("MobileApp", "IoT", "Campus", "React")

        req2, _ = Requirement.objects.get_or_create(
            post=recruit2,
            defaults={
                "year_min": 2,
                "year_max": 4,
                "description": "Frontend JavaScript/HTML/CSS skills or Python backend API integration."
            }
        )
        req2.req_faculty.add(faculties["Engineering"], faculties["Science"])
        req2.req_major.add(majors["Software Engineering"], majors["Computer Engineering"])

        team2, _ = Team.objects.get_or_create(recruit_post=post2, defaults={"team_leader": david})
        TeamMember.objects.get_or_create(team=team2, member=david)
        TeamMember.objects.get_or_create(team=team2, member=alex)
        TeamMember.objects.get_or_create(team=team2, member=sarah)

        chat2, _ = ChatGroup.objects.get_or_create(team=team2, defaults={"admin": david, "is_private": False})
        chat2.members.add(david, alex, sarah)

        # Add pre-populated chat messages to Team 2
        if not GroupMessage.objects.filter(group=chat2).exists():
            GroupMessage.objects.create(group=chat2, author=david, body="Welcome everyone to the Campus Shuttle project! 🚍")
            GroupMessage.objects.create(group=chat2, author=alex, body="Hey David! Got the repository cloned and WebSocket live update configured.")
            GroupMessage.objects.create(group=chat2, author=sarah, body="Hi team! Just uploaded the map UI mockups to Figma.")
            GroupMessage.objects.create(group=chat2, author=david, body="Looking fantastic Sarah! Let's integrate it this weekend.")

        # 5. Create Project 3: Completed Project Result Showcase
        post3, _ = Post.objects.get_or_create(
            heading="Autonomous Campus Delivery Rover Prototype",
            defaults={
                "user": alex,
                "content": (
                    "Project Complete! Our multidisciplinary team built a scale autonomous rover equipped with LiDAR, "
                    "ROS2 navigation stack, and an automated locker bay for contactless deliveries.\n"
                    "Winner of the 2024 University Innovation Showcase Award!"
                ),
                "finish": True,
            }
        )
        result3, _ = ResultPost.objects.get_or_create(post=post3)
        result3.tag.add("Robotics", "ROS2", "Hardware", "AwardWinner")

        team3, _ = Team.objects.get_or_create(recruit_post=post3, defaults={"team_leader": alex})
        TeamMember.objects.get_or_create(team=team3, member=alex)
        TeamMember.objects.get_or_create(team=team3, member=david)

        chat3, _ = ChatGroup.objects.get_or_create(team=team3, defaults={"admin": alex, "is_private": False})
        chat3.members.add(alex, david)
        if not GroupMessage.objects.filter(group=chat3).exists():
            GroupMessage.objects.create(group=chat3, author=alex, body="Project final presentation completed! Great work David! 🏆")
            GroupMessage.objects.create(group=chat3, author=david, body="Awesome working with you Alex. The ROS2 navigation demo blew the judges away!")

        # 5b. Create Project 4: Open Project for Applicant to Join (Sarah has NOT joined or applied)
        post4, _ = Post.objects.get_or_create(
            heading="Smart Campus Energy & Solar Monitor — Web Dashboard",
            defaults={
                "user": alex,
                "content": (
                    "We are building a smart campus energy monitor to visualize real-time solar generation, "
                    "building power consumption, and carbon reduction metrics.\n"
                    "Looking for a creative UI/UX designer and frontend developer to help design interactive analytics graphs, "
                    "mobile responsive layouts, and user alerts. Join our team!"
                ),
                "finish": False,
            }
        )
        recruit4, _ = RecruitPost.objects.get_or_create(post=post4, defaults={"status": True})
        recruit4.tag.add("GreenTech", "IoT", "Dashboard", "UI/UX")

        req4, _ = Requirement.objects.get_or_create(
            post=recruit4,
            defaults={
                "year_min": 1,
                "year_max": 4,
                "description": "Figma or frontend web prototyping skills. Open to all students passionate about sustainability."
            }
        )
        req4.req_faculty.add(faculties["Architecture & Design"], faculties["Engineering"], faculties["Science"])
        req4.req_major.add(majors["UI/UX Design"], majors["Software Engineering"], majors["Computer Engineering"])

        team4, _ = Team.objects.get_or_create(recruit_post=post4, defaults={"team_leader": alex})
        TeamMember.objects.get_or_create(team=team4, member=alex)

        chat4, _ = ChatGroup.objects.get_or_create(team=team4, defaults={"admin": alex, "is_private": False})
        chat4.members.add(alex)


        # 6. Create sample Feedbacks for MyStats Chart
        if not Feedback.objects.filter(receiver=alex).exists():
            Feedback.objects.create(
                team=team3,
                reviewer=david,
                receiver=alex,
                communication_pt=5,
                collaboration_pt=5,
                reliability_pt=4,
                technical_pt=5,
                empathy_pt=4,
                comment="Alex was an outstanding team leader who kept sprint goals clear and organized."
            )
        if not Feedback.objects.filter(receiver=sarah).exists():
            Feedback.objects.create(
                team=team2,
                reviewer=david,
                receiver=sarah,
                communication_pt=5,
                collaboration_pt=5,
                reliability_pt=5,
                technical_pt=4,
                empathy_pt=5,
                comment="Sarah delivered polished, user-friendly Figma UI components ahead of schedule!"
            )

        # Comments on posts
        PostComment.objects.get_or_create(
            post=post1,
            user=david,
            defaults={"comment": "Awesome hackathon problem statement! Upvoted.", "reaction": "thumbsup"}
        )

        self.stdout.write(self.style.SUCCESS("Interactive demo data successfully seeded!"))
        self.stdout.write(self.style.SUCCESS("Available Demo Personas:"))
        self.stdout.write(self.style.SUCCESS("  1. Alex Chen (Team Leader) -> username: alex_lead / password: password123"))
        self.stdout.write(self.style.SUCCESS("  2. Sarah Jenkins (Applicant) -> username: sarah_app / password: password123"))
        self.stdout.write(self.style.SUCCESS("  3. David Kim (ML Engineer)  -> username: david_ai  / password: password123"))
        self.stdout.write(self.style.SUCCESS("  4. Administrator           -> username: admin     / password: password123"))
